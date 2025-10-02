from pathlib import Path
import sys
sys.path.insert(1, str(Path(__file__).parent.parent))
from crowbar import *
from crowbar import Fpath
import crowbar
import html as htmllib
from sitetags import *
import tempfile
import os
from typing import Optional
from datetime import datetime
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles.pastie import PastieStyle


class CustomPastieStyle(PastieStyle):
    background_color = "#f9fafb"  # bg-gray-50 in tailwindcss


SITE_DIR = Path(__file__).parent.resolve()


with open(SITE_DIR / "site.css") as fh:
    CSS = [line.rstrip('\n') for line in fh.readlines()]

_formatter = HtmlFormatter(style=CustomPastieStyle)

@component
def site_header(emit):
    emit(
        div(
            {"class": "header-section"},
            div(
                {"class": "logo-placeholder"},
                img({"src": "logo.png"})
            ),
            div(
                h1(
                    {"class": "text-4xl font-bold mb-2"},
                    "CROWBAR"
                ),
                p(
                    {"class": "text-lg italic"},
                    '"When clever hacking fails, crude whacking prevails!"'
                )
            )
        )
    )


@component
def site_footer(emit):
    emit(
        hr({"class": "border-t border-gray-400 my-8"}),
        section("References"),
        div(
            {"class": "mb-4"},
            p(
                "Source Code: ",
                a({"href": "https://github.com/jwdevantier/crowbar"}, "github.com/jwdevantier/crowbar"),
            ),
            p(
                "Bug reports: ",
                a({"href": "https://github.com/jwdevantier/crowbar/issues"}, "github.com/jwdevantier/crowbar/issues"),
            ),
        ),
        div(
            {"class": "text-sm text-gray-600 mt-8"},
            p(
                "Generated on: ", datetime.now().strftime("%d/%m/%Y")
            ),
            p(
                "Version: ", crowbar.__version__
            )
        )
    )


@component
def section(emit, title):
    emit(
        div(
            {"class": "section-header mt-8 mb-4"},
            span(
                {"class": "font-bold"},
                f"# {title}"
            )
        )
    )


@component
def code_block(emit, code, lang: Optional[str] = None):
    """generate a box for displaying code, reads files if desired, applies HTML-escaping"""
    if code[0] == '@':
        with open(SITE_DIR / code[1:], mode="r") as fh:
            code = fh.read()
    elif isinstance(code, Path):
        with open(SITE_DIR / code, mode="r") as fh:
            code = fh.read()
    output: str
    if lang is None:
        output = htmllib.escape(code)
    else:
        output = highlight(code, get_lexer_by_name(lang), _formatter)
    emit(
        '<pre class="mb-6 bg-gray-50 p-4 border border-gray-300 text-sm overflow-x-auto">',
        output,
        '</pre>'
    )


class WithNamedTempFile:
    def __init__(self, prefix: Optional[str] = None, suffix: str = ".tmp"):
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, text=True)
        os.close(fd)
        self.__path = Path(path)

    @property
    def path(self) -> Path:
        return self.__path

    def __enter__(self) -> "WithNamedTempFile":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__path.unlink(missing_ok=True)


def resolve_path(p: Fpath) -> Path:
    if isinstance(p, Path):
        return SITE_DIR / p
    elif p[0] == '@':
        return SITE_DIR / p[1:]
    else:
        raise RuntimeError(f"expected a path or string path, got a string")


@component
def example(emit, code: Fpath, sep = None, lang: Optional[str] = None):
    code_path = resolve_path(code)
    emit(code_block(code, lang=lang))
    if sep is not None:
        emit(sep)
    p = CrowbarPreprocessor()
    with WithNamedTempFile() as tmp:
        p.process_file(code_path, tmp.path)
        with open(tmp.path, mode="r") as fh:
            emit(code_block(fh.read(), lang=lang))


# TODO: rewrite to align more with htt docs, use scribble terms
@component
def ul(emit, *elems):
    emit(
        fl,
        '<ul class="list-disc list-inside pl-4 space-y-1 mb-6">', nl, indent)
    for elem in elems:
        if isinstance(elem, str):
            emit(fl, f"<li>{elem}</li>")
        else:
            emit(fl, elem)
    emit(dedent, nl, '</ul>')


PARAGRAPH_ATTRS = {"class": "mb-6"}
MARK_START = htmllib.escape("<<crowbar")
MARK_OUT = htmllib.escape(">>")
MARK_END = htmllib.escape("<<end>>")

@component
def marker(emit, elem, desc):
    emit(f'<li><code class="text-sm">{elem}</code> &ndash; {desc}</li>')


site_body = body(
    {"class": "max-w-4xl mx-auto p-8"},
    site_header(),
    section("Abstract"),
    p(
        PARAGRAPH_ATTRS,
        "Crowbar is a code- and content-generation tool. It allows you to embed blocks", nl,
        "of Python inside a file to dynamically generate content inside an otherwise static file."
    ),
    section("What does it do?"),
    p(
        PARAGRAPH_ATTRS,
        "Crowbar principally works as a preprocessor. It scans your file for specially formatted "
        "blocks, evaluates the code in those blocks and inserts the output of those evaluations "
        "back into the source file."
    ),
    p(
        PARAGRAPH_ATTRS,
        "For example, say we wanted to generate some forward declarations of some C functions:"
    ),
    example(
        "@examples/intro_ex1.cpp",
        sep=p(
            PARAGRAPH_ATTRS,
            "After running, the file would look like so:"
        ),
        lang="cpp"
    ),
    p(
        PARAGRAPH_ATTRS,
        span(
        "Lines with ", code(MARK_START), ", ", code(MARK_OUT), " and ", code(MARK_END), " are ",
        emph("marker lines"), "."
        )
    ),
    code_block("@examples/block_example", lang="python"),
    p(
        PARAGRAPH_ATTRS,
        "Crowbar works for any language or file format which can support line- *or* multi-line comments "
        "in some way. Because of this, you have to indent each line of code in your blocks to match the "
        "start of the ", code(MARK_START), " marker, as shown above."
    ),
    p(
        PARAGRAPH_ATTRS,
        "Also, if you want to write the output elsewhere, you can also omit the code-blocks themselves "
        "from the output. This is helpful when writing small one-shot/passive generators, as you would "
        "for project starter templates and such. To omit the blocks from the output, run crowbar like so: "
    ),
    code_block("python --no-code-blocks input-file output-file"),
    section("Why use crowbar?"),
    ul(
        "BSD-2 license",
        "Single-file",
        "*Zero* external dependencies",
        "Supports Python 3.10 and up",
        "Use as preprocessor or use API in your own Python scripts for advanced generation",
        "Supports reuse and composition via definition of Components"
    ),
    section("The emit() API"),
    p(
        PARAGRAPH_ATTRS,
        code("emit()"), " is the equivalent of ", code("print()"), " for Crowbar. Not using ", code("print()"),
        " directly means Crowbar does not need to capture all stdout/stderr, and this means that you can use "
        "print-debugging and that output is not impacted by print statements scattered in the code you use. "
    ),
    p(
        PARAGRAPH_ATTRS,
        "Moreover, ", code("emit()"), " knows how to render Crowbar's components, and uses special marker ",
        "tokens to control newlines and indentation. The marker tokens are:"
    ),
    ul(
        marker("nl (newline)", "insert newline at this point"),
        marker("fl (fresh line)", "insert newline iff. line already has content on it"),
        marker("indent", "increase level of indentation used for new lines"),
        marker("dedent", "decrease level of indentation used for new lines"),
    ),
    p(
        PARAGRAPH_ATTRS,
        "This API makes formatting output much easier. In particular, abstracting indentation out this way "
        "permits components to be composable blocks, which may be nested in various ways and yet still the "
        "combined output is properly indented."
    ),
    section("Components - compose and reuse!"),
    p(
        PARAGRAPH_ATTRS,
        "Components is an additional feature that really separates Crowbar from tools like Cog. "
        "Think of components as building blocks, responsible for rendering some smaller element, and which "
        "can in turn delegate to other components. A component takes an ", code("emit()"), " function, but "
        "can take any additional arguments (positional and by keyword). When the component is invoked, the "
        "resulting value can be passed to ", code("emit()"), ", and indentation will just work&trade;"
    ),
    # TODO: minimal example
    # TODO: summary, what is a component
    # TODO: example with args
    section("Components Example"),
    p(
        PARAGRAPH_ATTRS,
        "Below we write a series of components which collectively make rendering a C function easy. Because we want to define several components, we put them in a separate Python file. This means we get full editor support: syntax highlighting, LSP, debugging and more."
    ),
    p(
        PARAGRAPH_ATTRS,
        "While this is a lot of code to print out one C function, it can pay off when you have a larger list of entities to render out."
    ),
    code_block("@examples/c_func_utils.py", lang="python"),
    example(
        "@examples/components_ex_c_func.c",
        sep=p(
            PARAGRAPH_ATTRS,
            "Finally, when asking Crowbar to process the file, we get:"
        ),
        lang="c"
    ),
    site_footer()
)


@component
def index_page(emit):
    emit(
        fl, "<!DOCTYPE html>",
        html(
            {"lang": "en"},
            head(
                meta({"charset": "UTF-8"}),
                meta({"name": "viewport", "content": "width=device-width, initial-scale=1.0"}),
                title("Crowbar - When Clever Hacking Fails, Crude Whacking Prevails!"),
                script({"src": "https://cdn.tailwindcss.com"}),
                style(*CSS, *(_formatter.get_style_defs(".highlight").split("\n")))
            ),
            site_body
        )
    )
