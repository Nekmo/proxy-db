from proxy_db.exceptions import UnknownExportFormat


class OutputBase:
    name = None

    def __init__(self, data):
        self.data = data

    def render(self):
        raise NotImplementedError

    def __str__(self):
        return self.render()


class LineOutput(OutputBase):
    name = 'line'

    def render(self):
        return '\n'.join(['{}'.format(line) for line in self.data])



EXPORT_OUTPUTS = [
    LineOutput,
]


def get_export_output_classes():
    return EXPORT_OUTPUTS


def get_export_output_class(name):
    try:
        return next(filter(lambda x: x.name == name, get_export_output_classes()))
    except StopIteration:
        raise UnknownExportFormat('Unknown format: {}. Use one of the following available formats: {}'.format(
            name, ', '.join(map(lambda x: x.name, get_export_output_classes()))
        ))


def get_export_output(name, data):
    return get_export_output_class(name)(data)
