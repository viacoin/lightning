from .plugin import Plugin
import itertools


def test_positional_inject():
    p = Plugin()
    rdict = {
        'id': 1,
        'jsonrpc':
        '2.0',
        'method': 'func',
        'params': {'a': 1, 'b': 2, 'kwa': 3, 'kwb': 4}
    }
    rarr = {
        'id': 1,
        'jsonrpc': '2.0',
        'method': 'func',
        'params': [1, 2, 3, 4]
    }

    def pre_args(plugin, a, b, kwa=3, kwb=4):
        assert (plugin, a, b, kwa, kwb) == (p, 1, 2, 3, 4)

    def in_args(a, plugin, b, kwa=3, kwb=4):
        assert (plugin, a, b, kwa, kwb) == (p, 1, 2, 3, 4)

    def post_args(a, b, plugin, kwa=3, kwb=4):
        assert (plugin, a, b, kwa, kwb) == (p, 1, 2, 3, 4)

    def post_kwargs(a, b, kwa=3, kwb=4, plugin=None):
        assert (plugin, a, b, kwa, kwb) == (p, 1, 2, 3, 4)

    def in_multi_args(a, request, plugin, b, kwa=3, kwb=4):
        assert request in [rarr, rdict]
        assert (plugin, a, b, kwa, kwb) == (p, 1, 2, 3, 4)

    def in_multi_mix_args(a, plugin, b, request=None, kwa=3, kwb=4):
        assert request in [rarr, rdict]
        assert (plugin, a, b, kwa, kwb) == (p, 1, 2, 3, 4)

    def extra_def_arg(a, b, c, d, e=42):
        """ Also uses a different name for kwa and kwb
        """
        assert (a, b, c, d, e) == (1, 2, 3, 4, 42)

    funcs = [pre_args, in_args, post_args, post_kwargs, in_multi_args]

    for func, request in itertools.product(funcs, [rdict, rarr]):
        p._exec_func(func, request)

    p._exec_func(extra_def_arg, rarr)
