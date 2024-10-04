from enum import Enum
from typing import NamedTuple

from pygments import lex
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles, get_style_by_name
from pygments.token import Token
from qtpy.QtCore import QEvent, QObject, QRect, Qt, Signal
from qtpy.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QKeyEvent,
    QPainter,
    QPalette,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from qtpy.QtWidgets import QPlainTextEdit, QWidget


class Language(NamedTuple):
    name: str
    alias: str


class CodeEdit(QPlainTextEdit):
    INDENT_SPACES_NUMBER = 4

    class Indent(Enum):
        WithSpaces = 0
        WithTabs = 1

    def __init__(self):
        super().__init__()
        self._indentation_mode = self.Indent.WithSpaces

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(14)
        self.setFont(font)

        self.highlighter = PygmentsSyntaxHighlighter(self.document())
        self.highlighter.styleChanged.connect(self._updatePalette)
        self._updatePalette()

        self.lineNumberArea = LineNumberArea(self)

    def keyPressEvent(self, e: QKeyEvent):
        if self._indentation_mode == self.Indent.WithSpaces:
            if e.key() == Qt.Key.Key_Tab:
                self._indentWithSpaces()
                return

            if e.key() == Qt.Key.Key_Backtab:
                self._unindentWithSpaces()
                return

        super().keyPressEvent(e)

    def languages(self):
        return (
            Language(name, aliases[0])
            for name, aliases, _, _ in get_all_lexers(plugins=False)
            if aliases
        )

    def themes(self):
        return get_all_styles()

    def setLanguage(self, language: Language | str):
        if isinstance(language, Language):
            language = language.alias

        self.highlighter.setLexer(language)

    def setTheme(self, theme):
        self.highlighter.setStyle(theme)

    def setShowLineNumbers(self, show: bool):
        self.lineNumberArea.setVisible(show)

    def setIndentationMode(self, mode: Indent):
        self._indentation_mode = mode

    def _updatePalette(self):
        self.setPalette(self.highlighter.stylePalette())

    def _indentWithSpaces(self):
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        cursor.insertText(" " * self.INDENT_SPACES_NUMBER)

    def _unindentWithSpaces(self):
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        text = cursor.block().text()
        n_spaces = len(text) - len(text.lstrip(" "))
        for _ in range(min(n_spaces, self.INDENT_SPACES_NUMBER)):
            cursor.deleteChar()


class PygmentsSyntaxHighlighter(QSyntaxHighlighter):
    DEFAULT_STYLE = "solarized-light"
    DEFAULT_LEXER = "python"

    styleChanged = Signal()

    def __init__(self, document):
        super().__init__(document)

        self.lexer = get_lexer_by_name(self.DEFAULT_LEXER)
        self.style = get_style_by_name(self.DEFAULT_STYLE)

        self.format_map = self.createFormatMap(self.style)

    def setStyle(self, style_name):
        self.style = get_style_by_name(style_name)
        self.format_map = self.createFormatMap(self.style)
        self.rehighlight()
        self.styleChanged.emit()

    def setLexer(self, lexer_name):
        self.lexer = get_lexer_by_name(lexer_name)
        self.rehighlight()

    def stylePalette(self) -> QPalette:
        style_bg_color = self.style.background_color
        style_for_text = self.style.style_for_token(Token.Text)
        style_for_comment = self.style.style_for_token(Token.Comment)

        palette = QPalette()
        bg_color = QColor(f"{style_bg_color}")
        text_color = QColor(f"#{style_for_text['color']}")
        comment_color = QColor(f"#{style_for_comment['color']}")
        palette.setColor(QPalette.ColorRole.Base, bg_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.PlaceholderText, comment_color)
        return palette

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        index = 0
        for token_type, token in lex(text, self.lexer):
            length = len(token)
            self.setFormat(index, length, self.format_map[token_type])
            index += length

    @staticmethod
    def createFormatMap(style):
        def to_fmt(token_style):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(f"#{token_style['color']}"))
            if token_style["bold"]:
                fmt.setFontWeight(QFont.Weight.Bold)
            if token_style["italic"]:
                fmt.setFontItalic(True)
            return fmt

        return {token_type: to_fmt(token_style) for token_type, token_style in style}


class LineNumberArea(QWidget):
    MIN_DIGITS = 3
    MARGIN_RIGHT = 3

    def __init__(self, editor: CodeEdit):
        super().__init__(editor)
        self.editor = editor
        self.editor.installEventFilter(self)
        self.editor.updateRequest.connect(self._onEditorUpdateRequest)
        self.editor.blockCountChanged.connect(self._updateWidth)
        self._updateWidth()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().base())

        block = self.editor.firstVisibleBlock()
        top = self._topOfBlock(block)
        bottom = top + self._blockHeight(block)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                lineNumber = str(block.blockNumber() + 1)
                self._paintNumber(painter, lineNumber, top)

            block = block.next()
            top = bottom
            bottom = top + self._blockHeight(block)

    def showEvent(self, event):
        super().showEvent(event)
        self._updateWidth()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._updateWidth()

    def eventFilter(self, watched: QObject, event: QEvent):
        if watched is not self.editor and event.type() != QEvent.Type.Resize:
            return False

        cr = self.editor.contentsRect()
        self.setGeometry(cr.left(), cr.top(), self.width(), cr.height())
        return False

    def _updateWidth(self, _=None):
        if not self.isVisible():
            self.editor.setViewportMargins(0, 0, 0, 0)
            return

        lineCount = self.editor.blockCount()
        digits = max(self.MIN_DIGITS, len(str(lineCount)))
        charWidth = self.fontMetrics().horizontalAdvance("9")
        space = 3 + self.MARGIN_RIGHT + charWidth * digits
        self.setFixedWidth(space)
        self.editor.setViewportMargins(space, 0, 0, 0)

    def _onEditorUpdateRequest(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

    def _topOfBlock(self, block):
        blockGeom = self.editor.blockBoundingGeometry(block)
        return int(round(blockGeom.translated(self.editor.contentOffset()).top()))

    def _blockHeight(self, block):
        return int(round(self.editor.blockBoundingRect(block).height()))

    def _paintNumber(self, painter, number, top):
        painter.setPen(self.palette().placeholderText().color())
        textRect = QRect(
            0, top, self.width() - self.MARGIN_RIGHT, self.fontMetrics().height()
        )
        painter.drawText(textRect, Qt.AlignmentFlag.AlignRight, number)
