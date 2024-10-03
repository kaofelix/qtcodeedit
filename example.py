import sys

from qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from qtcodeedit import CodeEdit

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    main_layout = QVBoxLayout()
    window.setLayout(main_layout)

    code_edit = CodeEdit()
    main_layout.addWidget(code_edit, stretch=1)

    control_layout = QHBoxLayout()
    main_layout.addLayout(control_layout)

    language_combobox = QComboBox()
    for name, alias in code_edit.languages():
        language_combobox.addItem(name, alias)

    language_combobox.currentIndexChanged.connect(
        lambda: code_edit.setLanguage(language_combobox.currentData())
    )
    language_combobox.setCurrentText("Python")
    control_layout.addWidget(language_combobox)

    theme_combobox = QComboBox()
    theme_combobox.addItems(code_edit.themes())
    theme_combobox.currentTextChanged.connect(code_edit.setTheme)
    theme_combobox.setCurrentText("solarized-light")
    control_layout.addWidget(theme_combobox)

    toggle_line_numbers_checkbox = QCheckBox(text="Show Line Numbers")
    toggle_line_numbers_checkbox.setChecked(True)
    toggle_line_numbers_checkbox.toggled.connect(code_edit.setShowLineNumbers)
    control_layout.addWidget(toggle_line_numbers_checkbox)

    window.show()

    sys.exit(app.exec_())
