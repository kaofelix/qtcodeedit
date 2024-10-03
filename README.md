# CodeEdit for Qt and Python

This is a simple code editor widget for Python and Qt supporting multiple languages and color
themes.

## Features

- Syntax and theming support powered by [Pygments](https://pygments.org), so any language and theme
  supported by it can be used
- Hide and show line numbers
- Spaces or tabs for indentation

## Implementation

The CodeEdit widget is based on `QPlainTextEdit` and syntax highlight is provided by a Pygments
based implementation of `QSyntaxHighlighter`. The line number implementation was based on [this
sample](https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html) from the Qt docs, with a
bit of cleanup and refactoring on my part.
