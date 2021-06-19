import enum

import nbformat


class CellType(enum.Enum):
    Markdown = 1
    Code = 2
    Raw = 3


class Cell():
    def __init__(self, cell) -> None:
        self._cell = cell

        self.cell_type = None
        self.source = None
        self.execution_count = None
        self.outputs = None

        self.init()

    def init(self):
        if self._cell.cell_type == "markdown":
            self.cell_type = CellType.Markdown
        elif self._cell.cell_type == "code":
            self.cell_type = CellType.Code
        else:
            self.cell_type = CellType.Raw

        self.source = self._cell.source

        if self.cell_type == CellType.Code:
            self.execution_count = self._cell.execution_count
            # TODO Add output class
            self.outputs = self._cell.outputs

    def get_highlight(self, begin: bool) -> str:
        highlight_text = ""

        if self.cell_type == CellType.Raw:
            return highlight_text

        if begin:
            highlight_text = "@begin="
        else:
            highlight_text = "@end="

        if self.cell_type == CellType.Markdown:
            highlight_text += "md@"
        else:
            highlight_text += "py@"

        return highlight_text

    def get_actions(self) -> str:
        actions = ""
        if self.cell_type == CellType.Code:
            actions += "Run cell | "
        actions += "Delete cell"
        return actions

    def get_execution_count(self) -> str:
        if self.cell_type != CellType.Code:
            return ""
        
        if self.execution_count != None:
            return f"[{self.execution_count}] "

        return "[ ] "

    def get_header(self) -> str:
        exec_count = self.get_execution_count()
        actions = self.get_actions()
        highlight_text = self.get_highlight(True)
        return exec_count + actions + highlight_text

    def get_footer(self) -> str:
        highlight_text = self.get_highlight(False)
        return highlight_text


class Notebook:
    def __init__(self, filename, bufnr, nvim, lua_bridge) -> None:
        self._nb = nbformat.read(filename, as_version=4)
        self._cells = []

        self._nvim = nvim
        self._lua_bridge = lua_bridge

        self.bufnr = bufnr

    def cells(self):
        if not self._cells:
            for cell in self._nb.cells:
                item = Cell(cell)
                self._cells.append(item)
                yield item
        else:
            for cell in self._cells:
                yield cell

    def draw_full(self):
        code = []
        for cell in self.cells():
            code.append(cell.get_header())

            code += cell.source.splitlines()

            code.append(cell.get_footer())

            code.append("")

        lines = self._nvim.api.buf_line_count(self.bufnr)
        self._lua_bridge.utils.buf_set_lines(self.bufnr, False, 0, lines, False, code, async_=True)


class NotebookManager:
    def __init__(self, nvim, lua_bridge) -> None:
        self._nvim = nvim
        self._lua_bridge = lua_bridge

        self.notebooks = {}

    def add_notebook(self, bufnr, filename) -> Notebook:
        nb = Notebook(filename, bufnr, self._nvim, self._lua_bridge)
        self.notebooks[bufnr] = nb
        return nb

    def del_notebook(self, bufnr) -> None:
        del self.notebooks[bufnr]


class AtomicCall:
    def __init__(self, nvim) -> None:
        self.nvim = nvim
        self.calls = []

    def merge(self, other):
        self.calls += other.calls

    def add_call(self, *args):
        if len(args) >= 2:
            self.calls.append([args[0], args[1:]])

    def call(self, async_=False):
        self.nvim.api.call_atomic(self.calls, async_=async_)


def create_jupyter_buffer(nvim):
        old_bufnr = nvim.current.buffer.number
        old_buf_name = nvim.api.buf_get_name(old_bufnr)

        buf = nvim.api.create_buf(True, False)
        bufnr = buf.number

        start_call = AtomicCall(nvim)
        start_call.add_call("nvim_command", f"buffer {bufnr}")
        start_call.add_call("nvim_command", f"bdelete {old_bufnr}")

        start_call.add_call("nvim_command", "setlocal nonumber")
        start_call.add_call("nvim_command", "setlocal signcolumn=no")
        start_call.add_call("nvim_command", "setlocal conceallevel=3")
        start_call.add_call("nvim_command", "setlocal concealcursor=nvic")

        start_call.add_call("nvim_buf_set_name", bufnr, old_buf_name)
        start_call.add_call("nvim_buf_set_option", bufnr, "modifiable", False)
        start_call.add_call("nvim_buf_set_option", bufnr, "buftype", "acwrite")
        start_call.add_call("nvim_command", "au BufWriteCmd <buffer>  call JupiterSave()")
        start_call.call(async_=True)

        return bufnr
