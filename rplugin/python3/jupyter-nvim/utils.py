import nbformat

from . import cell


class Notebook:
    def __init__(self, filename, bufnr, nvim, lua_bridge) -> None:
        self._nb = nbformat.read(filename, as_version=4)
        self.cells = []

        self._nvim = nvim
        self._lua_bridge = lua_bridge

        self.bufnr = bufnr

        # use _cell to not conflict with cell submodule
        for _cell in self._nb.cells:
            type = _cell.cell_type
            if type == "markdown":
                self.cells.append(cell.MarkdownCell(_cell))
            elif type == "code":
                self.cells.append(cell.CodeCell(_cell))
            else:
                self.cells.append(cell.RawCell(_cell))

    def draw_full(self):
        line_num = 1
        header = []

        code = []
        for _cell in self.cells:
            content = _cell.get_content()
            code += content
            header.append(line_num)
            line_num += len(content)

        lines = self._nvim.api.buf_line_count(self.bufnr)
        self._lua_bridge.utils.buf_set_lines(
            self.bufnr, False, 0, lines, False, code, async_=True
        )

        for head in header:
            self._nvim.funcs.sign_place(
                0, "Header", "JupyterNvimHeaderSign", self.bufnr, {"lnum": head}
            )


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


def prepare_jupyter_buffer(nvim):
    bufnr = nvim.current.buffer.number

    start_call = AtomicCall(nvim)
    start_call.add_call("nvim_command", "setlocal nonumber")
    start_call.add_call("nvim_command", "setlocal signcolumn=no")
    start_call.add_call("nvim_command", "setlocal conceallevel=3")
    start_call.add_call("nvim_command", "setlocal concealcursor=nvic")

    start_call.add_call("nvim_buf_set_option", bufnr, "modifiable", False)
    start_call.add_call("nvim_buf_set_option", bufnr, "buftype", "acwrite")
    start_call.add_call("nvim_command", "au BufWriteCmd <buffer>  call JupiterSave()")
    start_call.call(async_=True)

    return bufnr
