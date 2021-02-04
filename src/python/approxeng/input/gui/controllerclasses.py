# Simple command-line tool to list controller classes in a tabular form
from approxeng.input.controllers import get_controller_classes
from dataclasses import dataclass


def show_controller_classes():
    @dataclass(order=True)
    class ControllerMeta:
        vendor: int
        product: int
        name: str
        class_name: str

    def controller_meta():
        for id_string, c_class in get_controller_classes().items():
            vendor, product = id_string.split('-')
            name = c_class().__repr__()
            class_name = c_class.__name__
            yield ControllerMeta(int(vendor), int(product), name, class_name)

    # noinspection PyTypeChecker
    if meta_classes := sorted(controller_meta()):
        tuples = [(f'{meta.vendor:04x}', f'{meta.product:04x}', meta.name, meta.class_name) for meta in meta_classes]
        print(table(tuples, 'Vendor', 'Product', 'Controller Name', 'Class'))
    else:
        print('No available controller classes!')


def table(tuples, *headers):
    """
    Build a unicode box-character table to print the specified data

    :param tuples:
        A list of tuples of strings corresponding to rows in the table. Each tuple must be the same size, and also
        the same size as the list of headers
    :param headers:
        A list of header strings, the same length as the row tuples
    :return:
        A formatted string with newlines and using box characters to represent the data in tabular form
    """
    lengths = [max([len(items[i]) for items in tuples] + [len(headers[i])]) for i, _ in enumerate(headers)]

    def row(items):
        return '\u2502 ' + ' \u2502 '.join([f'{items[i]:{lengths[i]}}' for i, _ in enumerate(lengths)]) + ' \u2502'

    def furniture(left, mid, right):
        return left + mid.join('\u2500' * (length + 2) for length in lengths) + right

    def rows():
        yield furniture('\u250c', '\u252c', '\u2510')
        yield row(headers)
        yield furniture('\u251c', '\u253c', '\u2524')
        for t in tuples:
            yield row(t)
        yield furniture('\u2514', '\u2534', '\u2518')

    return '\n'.join(rows())
