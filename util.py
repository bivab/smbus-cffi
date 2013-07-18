def get_validator(tp, name):
    def f(x):
        if not isinstance(x, tp):
            raise TypeError("Expected %s" % name) 
    return f


validators = {}
for tp, name in [(int, 'integer'), (float, 'float'),
                  (str, 'string'), (dict, 'dict'), (list, 'list')]:
  validators[tp] = get_validator(tp, name)


def validate(**schema):
    def wrapper(fn):
        code = fn.func_code
        nargs = code.co_argcount
        varnames = code.co_varnames
        def validator(*args):
            if len(args) != nargs:
                raise TypeError("%s() takes exactly %d arguments (%d given)" %
                                (fn.__name__, nargs, len(args)))
            for name, typ in schema.iteritems():
                i = varnames.index(name)
                value = args[i]
                validators[typ](value)
            return fn(*args)
        return validator
    return wrapper
