import datetime
import json

from proxy_db.exceptions import UnknownExportFormat


try:
    import tabulate
except ImportError:
    tabulate = None


DEFAULT_COLUMNS = [
    'id', 'votes', 'country', 'protocol', 'created_at', 'updated_at', 'on_provider_at', 'providers'
]


def value_to_string(value):
    if isinstance(value, set):
        return ', '.join(value)
    elif isinstance(value, int):
        return f'{value}'
    return value


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class OutputBase:
    name = None
    default_columns = DEFAULT_COLUMNS

    def __init__(self, data, columns=None):
        self.data = data
        self.columns = columns or self.default_columns

    def get_rows(self):
        for item in self.data:
            item._set_providers()
            yield {key: value_to_string(item.get_param(key)) for key in self.columns}

    def render(self):
        raise NotImplementedError

    def __str__(self):
        return self.render()


class LineOutput(OutputBase):
    name = 'line'
    default_columns = ['proxy_with_credentials']

    def render(self):
        return '\n'.join([' '.join(row.values()) for row in self.get_rows()])


class JsonOutput(OutputBase):
    name = 'json'
    default_columns = OutputBase.default_columns + ['provider_requests__provider']

    def render(self):
        return json.dumps(list(self.get_rows()), cls=JsonEncoder, sort_keys=True, indent=4)


class TabulateBaseOutput(OutputBase):
    def render(self):
        return tabulate.tabulate(self.get_rows(), headers="keys", tablefmt=self.name.split('-')[0])


EXPORT_OUTPUTS = [
    LineOutput,
    JsonOutput,
]


def get_export_output_classes():
    classes = EXPORT_OUTPUTS
    tabulate_formats = []
    if tabulate is not None:
        tabulate_formats = tabulate._table_formats.keys()
    for tabulate_format in tabulate_formats:
        class TabulateOutput(TabulateBaseOutput):
            name = '{}-table'.format(tabulate_format)
        classes.append(TabulateOutput)
    return classes


def get_export_output_class(name):
    try:
        return next(filter(lambda x: x.name == name, get_export_output_classes()))
    except StopIteration:
        raise UnknownExportFormat('Unknown format: {}. Use one of the following available formats: {}'.format(
            name, ', '.join(map(lambda x: x.name, get_export_output_classes()))
        ))


def get_export_output(name, data, columns=None):
    return get_export_output_class(name)(data, columns)
