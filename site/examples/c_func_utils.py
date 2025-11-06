from crowbar import *

@component
def join(emit, sep=", ", *components):
    """Insert `sep` between each element."""
    if len(components) == 0:
        return
    if not isinstance(sep, list):
        sep = [sep]
    emit(*sep, components[0])
    for c in components[1:]:
        emit(*sep, c)

@component
def cfunc(emit, label=None, args=None, ret="void", body=None):
    if args is None:
        args = []
    if label is None:
        raise RuntimeError("must name the function")
    emit(
        f"{ret} {label}(",
        join([lc, ", ", lc], *args),
        lc, ") {",
        # alternatively; wrap elements to be indented in a list
        # [ body ]
        indent, body, dedent,
        "}"
    )

@component
def param(emit, ctype, label):
    emit(f"{ctype} {label}")

@component
def zebody(emit):
    emit(f"return x + y;")
