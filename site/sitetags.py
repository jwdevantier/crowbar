from crowbar import *
from crowbar import Component
from typing import Optional, Dict, Any


def lst_interleave_val(seq, lst):
    if not isinstance(seq, (list, tuple)):
        seq = [seq]
    return [x for item in lst for x in (*seq, item)]


def fmt_attrs(attrs: dict) -> str:
    _attrs = {**attrs}
    cls = _attrs.pop("cls", "")
    if cls:
        _attrs["class"] = cls
    return " ".join(f'{k}="{v}"' for k,v in _attrs.items())


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
        maybe_lc = lc if inline else None
        _body = lst_interleave_val(maybe_lc, children)
        if len(attrs.keys()) > 0:
            _attrs_str = fmt_attrs(attrs)
            tag_open = f"<{tag} {_attrs_str}>"
        else:
            tag_open = f"<{tag}>"
        emit(tag_open,
             _body,
             maybe_lc, f"</{tag}>")
    tagfn.__name__ = tag
    return tagfn


def voidelem(tag: str, default_attrs: Optional[Dict[str, Any]] = None, inline=False) -> Component:
    d_attrs = default_attrs or {}
    @component
    def tagfn(emit, attrs: Optional[Dict[str, Any]] = None):
        all_attrs = {**d_attrs}
        if attrs:
            all_attrs.update(**attrs)
        if all_attrs:
            _attrs_str = fmt_attrs(all_attrs)
            _tag = f"<{tag} {_attrs_str}/>"
        else:
            _tag = f"<{tag}/>"
        emit(_tag)
    tagfn.__name__ = tag
    return tagfn


# <<crowbar
# elems = [
#     "html", "head", "script", "style",
#     "body", "div",
#     "h1", "h2", "h3", "h4", "h5", "h6",
# ]
# for tag in elems:
#     emit(fl, f'{tag}: Component = elem("{tag}")')
# elems_inline = ["title", "pre", "span", "a", "p"]
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
p: Component = elem("p", inline=True)
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
    "p",
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
