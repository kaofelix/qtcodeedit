import pytest
from qtpy.QtGui import Qt, QTextCursor

from qtcodeedit import CodeEdit


@pytest.fixture
def code_edit(qtbot):
    code_edit = CodeEdit()
    qtbot.addWidget(code_edit)
    return code_edit


def test_smoke(code_edit):
    "Interact with the editor just to see that basically functionality doesn't raise Exceptions"
    code_edit.show()
    code_edit.insertPlainText("\n".join(["some text for a line"] * 1000))

    languages = list(code_edit.languages())
    themes = list(code_edit.themes())

    assert len(languages) > 0
    assert len(themes) > 0

    code_edit.setLanguage(languages[1])
    code_edit.setLanguage("markdown")

    code_edit.setTheme(themes[1])
    code_edit.setTheme("dracula")

    code_edit.setShowLineNumbers(False)
    assert code_edit.viewportMargins().left() == 0

    code_edit.setShowLineNumbers(True)
    assert code_edit.viewportMargins().left() > 0


class TestIndentation:
    def test_with_spaces(self, code_edit, qtbot):
        code_edit.insertPlainText("some line to indent")

        _move_cursor(code_edit, QTextCursor.MoveOperation.StartOfLine)
        qtbot.keyPress(code_edit, Qt.Key.Key_Tab)

        assert code_edit.toPlainText() == "    some line to indent"

    def test_with_spaces_from_anywhere_on_line(self, code_edit: CodeEdit, qtbot):
        code_edit.insertPlainText("some line to indent")

        _move_cursor(code_edit, QTextCursor.MoveOperation.Left, 3)
        qtbot.keyPress(code_edit, Qt.Key.Key_Tab)

        expected = "    some line to indent"
        assert code_edit.toPlainText() == expected
        assert code_edit.textCursor().columnNumber() == len(expected) - 3

    def test_unindent_with_spaces(self, code_edit: CodeEdit, qtbot):
        code_edit.insertPlainText("        some line to indent")

        _move_cursor(code_edit, QTextCursor.MoveOperation.Left, 3)
        qtbot.keyPress(code_edit, Qt.Key.Key_Backtab)

        expected = "    some line to indent"
        assert code_edit.toPlainText() == expected
        assert code_edit.textCursor().columnNumber() == len(expected) - 3

    def test_unindent_with_no_indentation_is_no_op(self, code_edit: CodeEdit, qtbot):
        code_edit.insertPlainText("some line to indent")

        _move_cursor(code_edit, QTextCursor.MoveOperation.Left, 3)
        qtbot.keyPress(code_edit, Qt.Key.Key_Backtab)

        assert code_edit.toPlainText() == "some line to indent"

    def test_with_tabs(self, code_edit, qtbot):
        code_edit.insertPlainText("some line to indent")
        code_edit.setIndentationMode(CodeEdit.Indent.WithTabs)

        _move_cursor(code_edit, QTextCursor.MoveOperation.StartOfLine)
        qtbot.keyPress(code_edit, Qt.Key.Key_Tab)

        assert code_edit.toPlainText() == "\tsome line to indent"


def _move_cursor(code_edit, move_op, n=1):
    text_cursor = code_edit.textCursor()
    text_cursor.movePosition(move_op, QTextCursor.MoveMode.MoveAnchor, n)
    code_edit.setTextCursor(text_cursor)
