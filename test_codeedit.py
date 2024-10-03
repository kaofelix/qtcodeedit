from qtcodeedit import CodeEdit


def test_smoke(qtbot):
    "Interact with the editor just to see that basically functionality doesn't raise Exceptions"
    code_edit = CodeEdit()
    qtbot.addWidget(code_edit)

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
