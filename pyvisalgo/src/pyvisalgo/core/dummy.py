class DummyVisualizer:
    def __getattr__(self, name):
        return self._do_nothing

    def _do_nothing(self, *args, **kwargs):
        return None

    def wait(self, *args, **kwargs):
        from .runner import set_action

        set_action("quit")
        return "quit"
