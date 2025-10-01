from crowbar import *

@component
def strjoin(emit, sep=", ", components=[]):
    if len(components) == 0:
        return
    emit(components[0])
    for c in components[1:]:
        emit(sep, c)

@component
def cfunc(emit, label=None, args=None, ret="void", body=None):
    if args is None:
        args = []
    if label is None:
        raise RuntimeError("must name the function")
    emit(
        fl,
        ret, f" {label}(",
        strjoin(sep=", ", components=args),
        ") {", indent, nl,
        body,
        fl, dedent, "}",
    )

@component
def param(emit, ctype, label):
    emit(f"{ctype} {label}")

@component
def zebody(emit):
    emit(f"return x + y;")
