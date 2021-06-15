class Notebook:
    def __init__(self) -> None:
        pass


class NotebookManager:
    def __init__(self):
        self.notebooks = {}

    def add_notebook(self, bufnr, nb):
        self.notebooks[bufnr] = nb

    def del_notebook(self, bufnr):
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

def buf_set_line(nvim, bufnr, modified, startIndex, endIndex, strict, replacement):
    line_call = AtomicCall(nvim)
    line_call.add_call("nvim_buf_set_option", bufnr, "modifiable", True)
    line_call.add_call("nvim_buf_set_lines", bufnr, startIndex, endIndex, strict, replacement)
    line_call.add_call("nvim_buf_set_option", "modifiable", False)
    if not modified:
        line_call.add_call("nvim_buf_set_option", bufnr, "modified", modified)
    return line_call
