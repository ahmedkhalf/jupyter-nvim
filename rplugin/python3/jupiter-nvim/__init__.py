import pynvim

import nbformat

@pynvim.plugin
class JupyterNvim:
    def __init__(self, nvim):
        self.nvim: pynvim.Nvim = nvim
        self.nvim.exec_lua("_jupiter_nvim = require('jupyter-nvim')")
        self.lua_bridge = self.nvim.lua._jupiter_nvim

    def get_cell_actions(self, type: str):
        if type == "markdown":
            return "Delete Cell "
        elif type == "code":
            return "Run Code | Delete Cell "
        return ""

    def get_highlight_text(self, type: str, begin: bool):
        highlight_text = ""
        if type == "markdown":
            if begin:
                highlight_text += self.get_cell_actions(type)
                highlight_text += "@begin=md@"
            else:
                highlight_text += "@end=md@"
        elif type == "code":
            if begin:
                highlight_text += self.get_cell_actions(type)
                highlight_text += "@begin=py@"
            else:
                highlight_text += "@end=py@"
        return highlight_text

    @pynvim.autocmd('BufAdd', pattern='*.ipynb', eval='expand("<afile>")')
    def openNotebook(self, filename):
        self.nvim.api.echo([["Openning Notebook: " + filename]], False, {})

        old_bufnr = self.nvim.current.buffer.number

        bufnr = self.lua_bridge.create_jupyter_buffer()
        self.nvim.command("bdelete " + str(old_bufnr))

        self.lua_bridge.add_syntax("python", "@begin=py@", "@end=py@", 'SpecialComment')
        self.lua_bridge.add_syntax("markdown", "@begin=md@", "@end=md@", 'SpecialComment')

        # self.nvim.command("hi! JupyterNvimCodeRegionComment guibg=none guifg=#2B2D37 ctermbg=none ctermfg=none")

        lines = self.nvim.api.buf_line_count(bufnr)

        nb = nbformat.read(filename, as_version=4)
        code = []

        for cell in nb.cells:
            # if cell.cell_type == 'code':
            #     if cell.execution_count != None:
            #         code.append(f"[{cell.execution_count}]")
            #     else:
            #         code.append("[_]")

            code.append(self.get_highlight_text(cell.cell_type, True))

            code += cell.source.splitlines()

            code.append(self.get_highlight_text(cell.cell_type, False))
            code.append("")

            # if cell.cell_type == 'code':
            #     if len(cell.outputs) > 0:
            #         code.append("Output:")

            #     for output in cell.outputs:
            #         if output.name == "stdout":
            #             code += output.text.splitlines()

        self.nvim.api.buf_set_lines(bufnr, 0, lines, False, code)

