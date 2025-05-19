class Figure:
    def __init__(self, *data):
        self.data = list(data)


class Sankey:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def line(df, x=None, y=None, color=None):
    return Figure({"type": "line", "x": x, "y": y, "color": color})


def bar(df, x=None, y=None):
    return Figure({"type": "bar", "x": x, "y": y})
