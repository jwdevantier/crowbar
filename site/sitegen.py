from crowbar import *

@component
def strjoin(emit, sep=", ", components=[]):
    if len(components) == 0:
        return
    emit(components[0])
    for c in components[1:]:
        emit(sep, c)


@component
def element(emit, tag, inline=False):
    emit(fl, "@component")
    emit(fl, f"def {tag}(emit, *args):", indent)
    emit(fl, "if len(args) == 0:", indent)
    emit(fl, f'emit("<{tag}/>")')
    emit(fl, 'return', dedent)
    emit(fl, "attrs = args[0] if isinstance(args[0], dict) else None")
    emit(fl, "children = args[1:] if attrs is not None else args")
    emit(fl, "if attrs and len(attrs.keys()) > 0:", indent)
    emit(fl, f'emit("<{tag} ", ')
    emit('''strjoin(" ", [f'{key}="{value}"' for key,value in attrs.items()]), ">", indent)''', dedent)
    emit(fl, 'else:', indent)
    emit(fl, f'''emit("<{tag}>", indent)''', dedent)
    emit(fl, 'for elem in children:', indent)
    if inline:
        emit(fl, 'emit(elem)', dedent)
        emit(fl, f'''emit(dedent, '</{tag}>')''')
    else:
        emit(fl, "emit(fl, elem)", dedent)
        emit(fl, f'''emit(fl, dedent, '</{tag}>', fl)''')
    emit(fl, dedent)
