from types import SimpleNamespace


class Data(SimpleNamespace):
    def __init__(self, file=None, data_file=None, **kwargs):
        if file is None and data_file is None:
            super().__init__(**kwargs)
            return

        from .runner import resolve_data

        data = resolve_data(file, kwargs, data_file=data_file)
        super().__init__(**data.__dict__)
