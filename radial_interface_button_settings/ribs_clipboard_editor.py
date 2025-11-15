from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor
from theme import Theme
from radial_interface_button_settings.ribs_button import RibsButton
from radial_interface_button_settings.ribs_label import RibsLabel
import enchant


class RibsClipboardEditor(QWidget):
    # Signal emitted when save button is clicked, with the text data
    data_saved = pyqtSignal(str)

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
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Instantiate RibsPlainTextEditor
        self.ribs_clipboard_input = self.RibsPlainTextEditor(self)

        # Add to layout to make it visible and ready for input
        self.layout.addWidget(self.ribs_clipboard_input)

        # Instantiate character counter label
        self.clipboard_editor_counter_label = RibsLabel("Character count: 0", "display", self)

        # Add counter label to layout
        self.layout.addWidget(self.clipboard_editor_counter_label, alignment=Qt.AlignLeft)

        # Connect text changed signal to update counter
        self.ribs_clipboard_input.textChanged.connect(self._update_character_counter)
        # Connect to update save button clickability
        self.ribs_clipboard_input.textChanged.connect(self._on_text_changed)

        # Instantiate save button at the bottom and center it
        self.ribs_clipboard_editor_save_btn = RibsButton("Save", self, clickable=False)
        # Connect save button to emit signal with data
        self.ribs_clipboard_editor_save_btn.clicked.connect(self._on_save_clicked)

        # Add controlled spacing before save button
        self.spacing_pixels = 10  # Variable to adjust spacing in pixels (0 = minimal spacing)
        self.layout.setSpacing(self.spacing_pixels)

        # Add save button at the bottom, centered
        self.layout.addWidget(self.ribs_clipboard_editor_save_btn, alignment=Qt.AlignCenter)

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

        def get_character_count(self):
            """
            Return the number of characters currently typed in the RibsPlainTextEditor.

            Returns:
                int: The total character count in the text editor
            """
            return len(self.toPlainText())

    def _update_character_counter(self):
        """
        Update the character counter label with current character count.
        Called whenever text changes in ribs_clipboard_input.
        """
        count = self.ribs_clipboard_input.get_character_count()
        self.clipboard_editor_counter_label.widget.setText(f"Character count: {count}")

    def _on_text_changed(self):
        """
        Update the save button clickability based on whether text is present.
        Called whenever text changes in ribs_clipboard_input.
        """
        text = self.ribs_clipboard_input.toPlainText().strip()
        self.ribs_clipboard_editor_save_btn.set_clickable(bool(text))

    def _on_save_clicked(self):
        """
        Handle save button click to emit the data_saved signal with current text.
        Called when ribs_clipboard_editor_save_btn is clicked.
        """
        text = self.ribs_clipboard_input.toPlainText().strip()
        self.data_saved.emit(text)
        # Close the editor window after saving
        self.close()
