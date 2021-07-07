import pynvim

from . import utils


@pynvim.plugin
class JupyterNvim:
    def __init__(self, nvim):
        self.nvim: pynvim.Nvim = nvim
        self.nvim.exec_lua("_jupiter_nvim = require('jupyter-nvim')")
        self.lua_bridge = self.nvim.lua._jupiter_nvim
        self.notebook_manager = utils.NotebookManager(self.nvim, self.lua_bridge)

        if not self.nvim.funcs.hlexists("JupyterNvimHeader"):
            self.nvim.command("highlight link JupyterNvimHeader CursorLine")
        self.nvim.funcs.sign_define(
            "JupyterNvimHeaderSign", {"linehl": "JupyterNvimHeader"}
        )

    @pynvim.function("JupiterSave")
    def writeNotebook(self, filename):
        self.nvim.api.buf_set_option(0, "modified", False)
        self.lua_bridge.utils.print_error(
            "Did not write file as jupiter-nvim doesn't have write support... yet.",
            True,
        )

    @pynvim.autocmd(
        "BufReadPost", pattern="*.ipynb", eval='expand("<afile>")', sync=True
    )
    def openNotebook(self, filename):
        bufnr = utils.create_jupyter_buffer(self.nvim)
        self.lua_bridge.utils.add_syntax(
            "python", "@begin=py@", "@end=py@", "SpecialComment", async_=True
        )
        self.lua_bridge.utils.add_syntax(
            "markdown", "@begin=md@", "@end=md@", "SpecialComment", async_=True
        )

        lines = self.nvim.api.buf_line_count(bufnr)
        self.lua_bridge.utils.buf_set_lines(
            bufnr, False, 0, lines, False, ["Loading..."]
        )

        def write_notebook():
            nb = self.notebook_manager.add_notebook(bufnr, filename)
            nb.draw_full()

        self.nvim.async_call(write_notebook)

    @pynvim.autocmd("VimEnter", pattern="*.ipynb", eval='expand("<afile>")')
    def vimOpened(self, filename):
        # We use this to handle cases where bufadd doesn't trigger as buffer is
        # added before vim enters
        self.openNotebook(filename)
