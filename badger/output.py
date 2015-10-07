from yaml import dump as yaml_dump


FORMATS = ['yaml', 'py']


def yaml(data, types, fn):
    with open(fn, 'w') as f:
        yaml_dump(data, f, default_flow_style=False)


def py(data, types, fn):
    code = """from numpy import array, zeros

metadata = {'hostname': '%(hostname)s',
            'time': '%(time)s'}
""" % {'hostname': data['metadata']['hostname'],
       'time': data['metadata']['time']}

    def fmt(v):
        if isinstance(v, str):
            return "'%s'" % v
        return str(v)

    size = []
    for p in data['parameters']:
        code += '{} = array([{}])\n'.format(p['name'], ', '.join(fmt(d) for d in p['values']))
        size.append(len(p['values']))
    size = '({})'.format(', '.join(str(s) for s in size))

    for k, vals in data['results'].items():
        code += '{} = zeros({}, dtype={})\n'.format(k, size, types[k])
        code += '{}.flat[:] = [{}]\n'.format(k, ', '.join(fmt(v) for v in vals))

    with open(fn, 'w') as f:
        f.write(code)
