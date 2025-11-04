from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor
from theme import Theme
import enchant


class RibsClipboardEditor(QWidget):
    def __init__(self, parent=None, window_title="Clipboard Editor"):
        """
        Initialize the RibsClipboardEditor window.

        Args:
            parent: Parent widget
            window_title: String to set as the window title (default: "Clipboard Editor")
        """
        super().__init__(parent, Qt.Window)
        self.setWindowTitle(window_title)

        # Set minimum window dimensions
        self.setMinimumSize(400, 400)

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Initialize the UI
        self.initUI()

    def initUI(self):
        """Initialize the RibsClipboardEditor UI."""
        # Set window title and basic layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Instantiate RibsPlainTextEditor
        self.ribs_clipboard_input = self.RibsPlainTextEditor(self)

        # Add to layout to make it visible and ready for input
        layout.addWidget(self.ribs_clipboard_input)

    class RibsPlainTextEditor(QPlainTextEdit):
        def __init__(self, parent=None):
            """
            Initialize the RibsPlainTextEditor widget using QPlainTextEdit.

            Args:
                parent: Parent widget
            """
            super().__init__(parent)

            # Get theme colors
            theme = Theme()
            self.colors = theme.get_colors()

            # Initialize spell checker
            self.spell_checker = self.SpellChecker(self.document())

            # Apply theme-based styling
            self._apply_style()

        def _apply_style(self):
            """Apply theme-based styling to the plain text editor."""
            background_color = self.colors.get("background", "#FFFFFF")
            text_color = self.colors.get("text", "#000000")
            border_color = self.colors.get("border", "#CCCCCC")

            # Apply stylesheet with theme colors
            self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: {background_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)

        class SpellChecker(QSyntaxHighlighter):
            def __init__(self, document):
                """
                Initialize the spell checker highlighter.

                Args:
                    document: The text document to highlight
                """
                super().__init__(document)

                # Try to initialize enchant dictionary
                try:
                    self.dictionary = enchant.Dict("en_US")  # English US dictionary
                except enchant.Error:
                    # Fallback if en_US is not available
                    try:
                        self.dictionary = enchant.Dict("en")
                    except enchant.Error:
                        # If no English dictionary is available, disable spell checking
                        self.dictionary = None

                # Set up highlighting format
                if self.dictionary:
                    self.mispell_format = QTextCharFormat()
                    self.mispell_format.setUnderlineColor(QColor("#FF0000"))  # Red underline
                    self.mispell_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)

            def highlightBlock(self, text):
                """
                Highlight misspelled words in the text block.

                Args:
                    text: The text block to check and highlight
                """
                if not self.dictionary:
                    return  # Skip if no dictionary available

                # Use regex to find word boundaries
                word_regex = QRegExp(r'\b\w+\b')
                pos = 0

                while (match := word_regex.indexIn(text, pos)) != -1:
                    word = word_regex.cap(0)

                    # Check if word is misspelled
                    if not self.dictionary.check(word):
                        # Apply formatting to highlight misspelled word
                        self.setFormat(match, len(word), self.mispell_format)

                    pos = match + len(word)
