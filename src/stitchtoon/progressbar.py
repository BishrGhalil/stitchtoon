class ProgressHandler:
    def __init__(self, prefix="", size=100):
        self.prefix = prefix
        self.size = size
        self._value = 0

    def start(self):
        pass

    def finish(self):
        pass

    @property
    def value(self):
        return 0

    @value.setter
    def value(self, value):
        pass

    def update(self, value, msg=""):
        pass


class DefaultCliProgress(ProgressHandler):
    def __init__(self, prefix="", size=60, out=None):
        from progress.bar import Bar

        if not out:
            from sys import stdout

            out = stdout
        super().__init__(prefix, size)
        self.bar = Bar(max=100, suffix="%(percent)d%% - %(eta)s second(s) left")
        self.out = out
        self.value = 0

    def start(self):
        self.value = 0
        self.bar.start()

    def finish(self):
        self.bar.finish()

    def update(self, value, msg=""):
        self.value = value
        self.bar.message = msg
        self.bar.next(value)
