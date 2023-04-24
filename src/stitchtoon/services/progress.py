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

        if not out:
            from sys import stdout
            out = stdout
        super().__init__(prefix, size)
        self.out = out

    def start(self):
        self.value = 0

    def show(self, msg):
        if msg:
            self.prefix = msg

        x = int(self.size * self.value / 100)
        print(
            "{} {}{}".format(self.prefix, u"🬋"* x, "-"* (self.size - x), self.value),
            end="\r",
            file=self.out,
            flush=True,
        )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        self._value = value

    def finish(self):
        print("\n", flush=True, file=self.out)

    def update(self, value, msg=""):
        self.value = value
        self.show(msg)