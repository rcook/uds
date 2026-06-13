from click import BadParameter
from pytest import raises

from bygge.util.cli import NamedChoice


def test_named_choice_basics() -> None:
    choice = NamedChoice[int]([("one", 1), ("two", 2), ("three", 3)])

    assert choice.convert("one", param=None, ctx=None) == 1
    assert choice.convert("two", param=None, ctx=None) == 2
    assert choice.convert("three", param=None, ctx=None) == 3

    with raises(BadParameter):
        _ = choice.convert("(unknown)", param=None, ctx=None)

    assert choice.get_metavar(param=None, ctx=None) == "[one|two|three]"

    assert choice.get_missing_message(param=None, ctx=None) == "Choose from one, two, three."
