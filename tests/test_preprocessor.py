from crowbar import *
from crowbar import Fpath
from crowbar import UnexpectedEOF
from crowbar import CodeEvalError
from crowbar import IndentationError
from crowbar import FileParseError
from crowbar import InvalidOutputPath
from test_utils.utils import WithNamedTempFile, slurp
from pathlib import Path
import pytest
from contextlib import contextmanager


CWD = Path(__file__).parent


@contextmanager
def xraises(*args, **kwargs):
    """pytest.raises, except it unwraps FileParseError"""
    with pytest.raises(*args, **kwargs) as exc_info:  # type: ignore
        try:
            yield exc_info
        except FileParseError as e:
            if e.__cause__:
                raise e.__cause__
            raise


def process_file(input: Fpath, omit_code_blocks: bool = False) -> str:
    with WithNamedTempFile() as tmp:
        p = CrowbarPreprocessor()
        p.process_file(input, tmp.path, omit_code_blocks=omit_code_blocks)
        return slurp(tmp.path)


def test_invalid_output_path():
    """If something at output path exists, ensure it's a file, otherwise error out"""
    import tempfile

    with WithNamedTempFile() as tmp:
        with open(tmp.path, mode="w") as fh:
            fh.write("hello")
        with tempfile.TemporaryDirectory(prefix="crowbar") as tmpdir:
            p = CrowbarPreprocessor()
            with pytest.raises(InvalidOutputPath):
                p.process_file(tmp.path, tmpdir)


def test_no_code_blocks__same_file_error():
    """Ensure that you cannot pass `--no-code-blocks`, and thus strip out code blocks, when writing back to the same file"""
    with WithNamedTempFile() as tmp:
        with open(tmp.path, mode="w") as fh:
            fh.write("hello")
        p = CrowbarPreprocessor()
        with pytest.raises(
            ValueError, match=r"must be writing to a \*different\* file"
        ):
            p.process_file(tmp.path, omit_code_blocks=True)


def test_no_code_blocks__test_output():
    assert process_file(CWD / "preproc_no_code_blocks", omit_code_blocks=True) == slurp(
        CWD / "preproc_no_code_blocks.expected"
    )


def test_global_emit():
    """Test the emit helper function available in preprocessor mode."""
    assert process_file(CWD / "preproc_global_emit") == slurp(
        CWD / "preproc_global_emit.expected"
    )


def test_multiple_emits_inline():
    """Ensure emit('hello, '); emit('world!') renders 'hello, world!'"""
    assert process_file(CWD / "preproc_multiple_emits_inline") == slurp(
        CWD / "preproc_multiple_emits_inline.expected"
    )


def test_file_unchanged_on_parse_error():
    # we know that IF the file would be written, whatever was in the output
    # sections of existing blocks would have been cleared and whatever output
    # the blocks generated would be in its stead.
    contents = """\n
hello, world

# <<crowbar
# print('hey')
# >>
output from last run
# <<end>>

more stuff

# <<crowbar
#print('will not work')
# >>
output from last run, also
# <<end>>"""
    with WithNamedTempFile() as tmp:
        with open(tmp.path, mode="w") as fh:
            fh.write(contents)
        p = CrowbarPreprocessor()
        with xraises(CodeEvalError):
            p.process_file(tmp.path)
        new_contents = slurp(tmp.path)
        assert new_contents == contents


def test_parse_line_comments():
    """Parse blocks using various types of line comments."""
    assert process_file(CWD / "preproc_parse_line_comments") == slurp(
        CWD / "preproc_parse_line_comments.expected"
    )


def test_parse_multiline_comments():
    """Parse blocks using various types of multiline comments."""
    assert process_file(CWD / "preproc_parse_multiline_comments") == slurp(
        CWD / "preproc_parse_multiline_comments.expected"
    )


def test_parse_base_indent():
    """Test ability to determine base indentation"""
    assert process_file(CWD / "preproc_base_indent") == slurp(
        CWD / "preproc_base_indent.expected"
    )


def test_statefulness():
    """State defined in one block carries over into the next block"""
    assert process_file(CWD / "preproc_state") == slurp(CWD / "preproc_state.expected")


def test_inline_blocks():
    """Test ability to put marker START, code and code end into same line"""
    assert process_file(CWD / "preproc_inline") == slurp(
        CWD / "preproc_inline.expected"
    )


def test_eof_code_section():
    """Raise error if EOF while looking for end of block's code section'"""
    with xraises(UnexpectedEOF):
        process_file(CWD / "preproc_eof_code")


def test_eof_output_section():
    """Raise error if EOF while looking for end of block's output section'"""
    with xraises(UnexpectedEOF):
        process_file(CWD / "preproc_eof_out")


def test_code_indent_insufficient():
    with xraises(CodeEvalError):
        process_file(CWD / "preproc_code_indent_insufficient")


def test_code_indent_insufficient_multiple_1():
    """Multiple lines, all the same prefix, so we will get an incorrectly extracted block of code which will cause an eval error"""
    with xraises(CodeEvalError):
        process_file(CWD / "preproc_code_indent_insufficient_multiple_1")


def test_code_indent_insufficient_multiple_2():
    """Multiple lines, different prefixes, so we will raise an indentation error"""
    with xraises(IndentationError):
        process_file(CWD / "preproc_code_indent_insufficient_multiple_2")
