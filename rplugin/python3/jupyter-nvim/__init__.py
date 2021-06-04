import pynvim

import nbformat

@pynvim.plugin
class JupyterNvim:
    def __init__(self, nvim):
        self.nvim: pynvim.Nvim = nvim
        self.nvim.exec_lua("_jupiter_nvim = require('jupyter-nvim')")
        self.lua_bridge = self.nvim.lua._jupiter_nvim

    def get_cell_stdout(self, cell):
        cell_stdout = ""
        if cell.cell_type == 'code':
            if len(cell.outputs) > 0:
                cell_stdout += "Output:\n"

            for output in cell.outputs:
                if output.name == "stdout":
                    cell_stdout += output.text
                    
        return cell_stdout

    def get_execution_count(self, cell):
        execution_count = ""
        if cell.cell_type == 'code':
            if cell.execution_count != None:
                execution_count += f"[{cell.execution_count}] "
            else:
                execution_count += "[ ] "
        return execution_count

    def get_cell_actions(self, cell):
        # Currently cell actions are purely here for cosmetic purposes, later
        # in the project you will be able to click on them and produce an
        # action.
        type = cell.cell_type

        if type == "markdown":
            return "Delete Cell"
        elif type == "code":
            return "Run Code | Delete Cell"
        return ""

    def get_highlight_text(self, cell, begin: bool):
        type = cell.cell_type
        highlight_text = ""

        if begin:
            highlight_text = "@begin="
        else:
            highlight_text = "@end="

        if type == "markdown":
            highlight_text += "md@"
        elif type == "code":
            highlight_text += "py@"
        else:
            # Shouldn't happen, but just in case...
            highlight_text = ""

        return highlight_text

    def get_block_header(self, cell):
        exec_count = self.get_execution_count(cell)
        cell_actions = self.get_cell_actions(cell)
        highlight_text = self.get_highlight_text(cell, True)

        return exec_count + cell_actions + highlight_text

    def get_block_footer(self, cell):
        highlight_text = self.get_highlight_text(cell, False)
        stdout = self.get_cell_stdout(cell)

        return (highlight_text + stdout).splitlines()

    @pynvim.function("JupiterSave")
    def writeNotebook(self, filename):
        self.nvim.api.buf_set_option(0, "modified", False)
        self.lua_bridge.print_error(
            "Did not write file as jupiter-nvim doesn't have write support... yet."
        )

    @pynvim.autocmd('BufAdd', pattern='*.ipynb', eval='expand("<afile>")')
    def openNotebook(self, filename):
        old_bufnr = self.nvim.current.buffer.number
        old_buf_name = self.nvim.api.buf_get_name(old_bufnr)

        bufnr = self.lua_bridge.create_jupyter_buffer()
        self.nvim.command("bdelete " + str(old_bufnr))
        self.nvim.api.buf_set_name(bufnr, old_buf_name)

        nb = nbformat.read(filename, as_version=4)
        code = []

        for cell in nb.cells:
            code.append(self.get_block_header(cell))

            code += cell.source.splitlines()

            code += self.get_block_footer(cell)
            code.append("")

        lines = self.nvim.api.buf_line_count(bufnr)
        self.lua_bridge.buf_set_lines(bufnr, False, 0, lines, False, code)

    @pynvim.autocmd('VimEnter', pattern='*.ipynb', eval='expand("<afile>")')
    def vimOpened(self, filename):
        # We use this to handle cases where bufadd doesn't trigger as buffer is
        # added before vim enters
        self.openNotebook(filename)
