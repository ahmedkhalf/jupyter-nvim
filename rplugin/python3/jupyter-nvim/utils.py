import nbformat

from . import cell


class Notebook:
    def __init__(self, filename, bufnr, nvim, lua_bridge) -> None:
        self._nb = nbformat.read(filename, as_version=4)
        self._cells = []

        self._nvim = nvim
        self._lua_bridge = lua_bridge

        self.bufnr = bufnr


        for _cell in self._nb.cells:
            type = _cell.cell_type
            if type == "markdown":
                self._cells.append(cell.MarkdownCell(_cell))
            elif type == "code":
                self._cells.append(cell.CodeCell(_cell))
            else:
                self._cells.append(cell.RawCell(_cell))

    def cells(self):
        for cell in self._cells:
            yield cell

    def draw_full(self):
        code = []
        for cell in self.cells():
            code += cell.get_content()

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
