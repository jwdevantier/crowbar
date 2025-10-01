from crowbar import *
from crowbar import Component
from typing import Optional, Dict, Any


@component
def strjoin(emit, sep=", ", components=[]):
    if len(components) == 0:
        return
    emit(components[0])
    for c in components[1:]:
        emit(sep, c)


def elem(tag: str, default_attrs: Optional[Dict[str, Any]]=None, inline=False) -> Component:
    d_attrs = default_attrs or {}
    @component
    def tagfn(emit, *args):
        if len(args) == 0:
            # only void elements may be self-closing.
            emit(f"<{tag}></{tag}>")
            return
        _attrs = args[0] if isinstance(args[0], dict) else None
        children = args[1:] if _attrs else args
        attrs = {**d_attrs}
        if _attrs:
            attrs.update(**_attrs)
        maybe_fl = fl if len(children) > 0 and not inline else None
        if len(attrs.keys()) > 0:
            emit(maybe_fl, f"<{tag} ", strjoin(" ", [
                f'{key}="{value}"'
                for key, value in attrs.items()]),
                 ">", indent)
        else:
            emit(maybe_fl, f"<{tag}>", indent)
        for elem in children:
            emit(maybe_fl, elem)
        emit(maybe_fl, dedent, f"</{tag}>", maybe_fl)
    tagfn.__name__ = tag
    return tagfn


def voidelem(tag: str, default_attrs: Optional[Dict[str, Any]] = None, inline=False) -> Component:
    d_attrs = default_attrs or {}
    maybe_fl = None if inline else fl
    @component
    def tagfn(emit, attrs: Optional[Dict[str, Any]] = None):
        all_attrs = {**d_attrs}
        if attrs:
            all_attrs.update(**attrs)
        if all_attrs:
            emit(maybe_fl, f"<{tag} ", strjoin(" ", [
                f'{key}="{value}"'
                for key, value in all_attrs.items()]),
                 "/>", maybe_fl)
        else:
            emit(maybe_fl, f"<{tag}/>", maybe_fl)
    tagfn.__name__ = tag
    return tagfn


# <<crowbar
# elems = [
#     "html", "head", "script", "style",
#     "body", "div", "p",
#     "h1", "h2", "h3", "h4", "h5", "h6",
# ]
# for tag in elems:
#     emit(fl, f'{tag}: Component = elem("{tag}")')
# elems_inline = ["title", "pre", "span", "a"]
# for tag in elems_inline:
#     emit(fl, f'{tag}: Component = elem("{tag}", inline=True)')
# voidelems = [
#     "hr", "img", "input", "link", "br", "input", "meta",
# ]
# for tag in voidelems:
#     emit(fl, f'{tag}: Component = voidelem("{tag}")')
# >>
html: Component = elem("html")
head: Component = elem("head")
script: Component = elem("script")
style: Component = elem("style")
body: Component = elem("body")
div: Component = elem("div")
p: Component = elem("p")
h1: Component = elem("h1")
h2: Component = elem("h2")
h3: Component = elem("h3")
h4: Component = elem("h4")
h5: Component = elem("h5")
h6: Component = elem("h6")
title: Component = elem("title", inline=True)
pre: Component = elem("pre", inline=True)
span: Component = elem("span", inline=True)
a: Component = elem("a", inline=True)
hr: Component = voidelem("hr")
img: Component = voidelem("img")
input: Component = voidelem("input")
link: Component = voidelem("link")
br: Component = voidelem("br")
input: Component = voidelem("input")
meta: Component = voidelem("meta")
# <<end>>
code = elem("code", default_attrs={"class": "text-sm"}, inline=True)
emph = elem("emph", {"class": "italic"}, inline=True)

__all__ = [
    # <<crowbar
    # all_elems = [*elems, *elems_inline, *voidelems]
    # for elem in all_elems:
    #     emit(fl, f'"{elem}",')
    # >>
    "html",
    "head",
    "script",
    "style",
    "body",
    "div",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "title",
    "pre",
    "span",
    "a",
    "hr",
    "img",
    "input",
    "link",
    "br",
    "input",
    "meta",
    # <<end>>
    "code",
    "emph",
]
