from crowbar import *
import pytest
from test_utils.utils import WithNamedTempFile, slurp


def test_kw_args():
    """Test ability to pass keyword args to component"""

    @component
    def greet(emit, name="thing"):
        emit(f"hello, {name}!")

    out = []
    emit = Emitter(writer=out.append)

    emit(greet(name="gordon"))
    assert "".join(out) == "hello, gordon!"

    out.clear()
    emit = Emitter(writer=out.append)
    emit(greet(name="alex"))
    assert "".join(out) == "hello, alex!"

    out.clear()
    emit = Emitter(writer=out.append)
    emit(greet())
    assert "".join(out) == "hello, thing!"

    out.clear()
    emit = Emitter(writer=out.append)
    emit(greet())
    assert "".join(out) == "hello, thing!"


def test_args():
    """test ability to pass positional args to component"""

    @component
    def greet(emit, name):
        emit(f"hello, {name}!!")

    out = []
    emit = Emitter(writer=out.append)
    emit(greet("gordon"))
    assert "".join(out) == "hello, gordon!!"

    out.clear()
    emit = Emitter(writer=out.append)
    emit(greet("alex"))
    assert "".join(out) == "hello, alex!!"


def test_render_inline():
    """If components are separated by the `lc` (line-continue) marker, then they are
    the next element starts on the same line as the previous element."""
    counter = 1

    @component
    def greet(emit, name=None):
        nonlocal counter
        if name is None:
            name = f"thing{counter}"
            counter += 1
        emit(f"hello, {name}!")

    out = []
    emit = Emitter(writer=out.append)

    # single component
    emit(greet(), lc)
    emit(greet())
    assert "".join(out) == "hello, thing1!hello, thing2!"


def test_render_multiple_elements():
    """If components don't use nl, fl, or lc control markers,
    then two or more components are separated by newlines (and appropriately indented)
    """

    counter = 1

    @component
    def greet(emit, name=None):
        nonlocal counter
        if name is None:
            name = f"thing{counter}"
            counter += 1
        emit(f"hello, {name}!")

    out = []
    emit = Emitter(writer=out.append)

    # single component
    emit(greet())
    emit(greet())
    assert "".join(out) == "hello, thing1!\nhello, thing2!"


def test_indents():
    out = []

    @component
    def main(emit):
        emit(
            "hello1",
            indent,
            "hello2",
            indent,
            "hello3",
            dedent,
            "hello2",
            dedent,
            "hello1",
        )

    emit = Emitter(writer=out.append, base_indent="", indent_step="   ")
    emit(main())
    assert (
        "".join(out)
        == """\
hello1
   hello2
      hello3
   hello2
hello1"""
    )

    # try a different base indent
    out = []
    emit = Emitter(writer=out.append, base_indent="  ", indent_step="    ")
    emit(main())
    assert (
        "".join(out)
        == """\
  hello1
      hello2
          hello3
      hello2
  hello1"""
    )


def test_indent_nl_unordered():
    """Ensure that output is same regardless of whether emitting nl followed by {dedent,indent} or vice versa"""

    @component
    def main1(emit):
        emit(
            "hello1",
            indent,
            nl,
            "hello2",
            indent,
            nl,
            "hello3",
            dedent,
            nl,
            "hello2",
            dedent,
            nl,
            "hello1",
        )

    out1 = []
    emit = Emitter(writer=out1.append, base_indent="", indent_step="   ")
    emit(main1())

    @component
    def main2(emit):
        # same as main, though we swap the order of nl/{indent,dedent}
        # should produce the same result.
        emit(
            "hello1",
            nl,
            indent,
            "hello2",
            nl,
            indent,
            "hello3",
            nl,
            dedent,
            "hello2",
            nl,
            dedent,
            "hello1",
        )

    out2 = []
    emit = Emitter(writer=out2.append, base_indent="", indent_step="   ")
    emit(main2())

    assert "".join(out1) == "".join(out2)


def test_composing_components():
    """Tests ability to compose components into larger structures"""

    @component
    def strjoin(emit, sep=", ", components=[]):
        if len(components) == 0:
            return
        emit(lc, components[0])
        for c in components[1:]:
            emit(lc, sep, lc, c)

    @component
    def cfunc(emit, label=None, args=None, ret="void", body=None):
        if args is None:
            args = []
        if label is None:
            raise RuntimeError("must name the function")
        # TODO: remove or revisit
        # if body and not isinstance(body, Component):
        #     raise RuntimeError("body MUST be None or a Component")

        emit(
            ret,
            lc,
            f" {label}(",
            strjoin(sep=", ", components=args),
            lc,
            ") {",
            indent,
            body,
            dedent,
            "}",
        )

    @component
    def param(emit, ctype=None, label=None):
        if ctype is None or label is None:
            raise RuntimeError("must provide `label` and `ctype` args")
        emit(f"{ctype} {label}")

    @component
    def zebody(emit):
        emit(f"return x + y;")

    out = []
    emit = Emitter(writer=out.append, indent_step="   ")
    emit(
        cfunc(
            label="add",
            args=[param(ctype="int", label="x"), param(ctype="int", label="y")],
            ret="int",
            body=zebody(),
        ),
    )

    assert (
        "".join(out)
        == """\
int add(int x, int y) {
   return x + y;
}"""
    )


def test_emit_render_args():
    @component
    def asval(emit, val=None):
        emit(val)

    @component
    def greet(emit, thing="thing"):
        emit(f"hello, {thing}!")

    def stringify_result(val):
        out = []
        emit = Emitter(writer=out.append)
        emit(
            asval(val=val),
        )
        return "".join(out)

    assert stringify_result(None) == ""
    assert stringify_result(3.14) == "3.14"
    assert stringify_result(3) == "3"
    assert stringify_result("Gordon") == "Gordon"
    assert stringify_result(True) == "True"
    assert stringify_result(greet()) == "hello, thing!"


def test_err_if_emitting_component_type():
    """
    emit() requires ComponentClosures, that is, a component for which
    the context (arguments) has already been provided and which only
    requires an emit function then to write to.
    """

    @component
    def smth(emit):
        emit("hello")

    @component
    def main(emit, other=None):
        emit(other)

    out = []
    emit = Emitter(writer=out.append)
    with pytest.raises(TypeError, match="does not accept raw components"):
        emit(main(other=smth))


def test_emit_state_retained_across_render_calls():
    @component
    def render1(emit):
        emit("render1")

    @component
    def render2(emit):
        emit(fl, "render2")

    out = []
    emit = Emitter(writer=out.append)
    emit(render1())
    emit(render2())
    assert (
        "".join(out)
        == """\
render1
render2"""
    )
