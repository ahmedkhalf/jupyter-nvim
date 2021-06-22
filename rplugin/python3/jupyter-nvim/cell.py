class Section:
    def __init__(self) -> None:
        self.text = []
        self.length = 0

    def set_text(self, text: str, oneline: bool = False):
        # TODO use get/set ?
        if oneline:
            self.length = 1
            self.text = [text]
        else:
            split_text = text.splitlines()
            self.length = len(split_text)
            self.text = split_text


class Cell:
    def __init__(self, cell) -> None:
        self._cell = cell
        self._metadata = self._cell.metadata

        self.header = Section()
        self.source = Section()
        self.footer = Section()

        self.init_header()
        self.init_source()
        self.init_footer()

    def init_header(self):
        raise NotImplementedError()

    def init_source(self):
        self.source = Section()
        self.source.set_text(self._cell.source)

    def init_footer(self):
        raise NotImplementedError()

    def get_content(self):
        return self.header.text + self.source.text + self.footer.text


class MarkdownCell(Cell):
    def __init__(self, cell) -> None:
        super().__init__(cell)

    def init_header(self):
        actions = "Delete Cell "
        highlight = "@begin=md@"

        self.header.set_text(actions + highlight, oneline=True)

    def init_footer(self):
        self.footer.set_text("@end=md@")


class CodeCell(Cell):
    def __init__(self, cell) -> None:
        self.outputs = cell.outputs  # list of output dicts
        self.init_output()

        self.execution_count = cell.execution_count

        super().__init__(cell)


    def init_header(self):
        exec_count = f"[{self.execution_count or ' '}] "
        actions = "Run Code | Delete Cell "
        highlight = "@begin=py@"

        self.header.set_text(exec_count + actions + highlight, oneline=True)

    def init_footer(self):
        if len(self.outputs) == 0:
            self.footer.set_text("@end=py@")
        else:
            self.footer.set_text("@end=py@" + "Output:")

    def init_output(self):
        output_text = []
        for output in self.outputs:
            if output.output_type == "stream":
                output_text += output.text.splitlines()
            # elif output.output_type == "error":
            #     for frame in output.traceback:
            #         output_text += frame.splitlines()
        self.output_section = output_text


    def get_content(self):
        content = self.header.text + self.source.text + self.footer.text
        if len(self.outputs) != 0:
            content += self.output_section + [""]
        return content


class RawCell(Cell):
    def __init__(self, cell) -> None:
        super().__init__(cell)


    def init_header(self):
        actions = "Delete Cell"

        self.header.set_text(actions, oneline=True)

    def init_footer(self):
        return

