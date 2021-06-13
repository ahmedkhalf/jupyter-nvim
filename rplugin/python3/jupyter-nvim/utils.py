class AtomicCall:
    def __init__(self, nvim) -> None:
        self.nvim = nvim
        self.calls = []

    def add_call(self, *args):
        if len(args) >= 2:
            self.calls.append([args[0], args[1:]])

    def call(self, async_=False):
        self.nvim.api.call_atomic(self.calls, async_=async_)

