from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QRegExp, QTimer, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor
from theme import Theme
from radial_interface_button_settings.ribs_button import RibsButton
from radial_interface_button_settings.ribs_label import RibsLabel
import enchant


class RibsTooltipEditor(QWidget):
    # Define the signal at class level
    save_data_signal = pyqtSignal(str)
    
    # Class attribute for window title
    window_title = "Tooltip Editor"

    def __init__(self, parent=None, window_title=None):
        """
        Initialize the RibsTooltipEditor window.

        Args:
            parent: Parent widget
            window_title: String to set as the window title (default: "Tooltip Editor")
        """
        super().__init__(parent, Qt.Window)
        self.setWindowTitle(window_title or self.window_title)

        # Set minimum window dimensions
        self.setMinimumSize(400, 100)

        # Max characters
        self.max_chars = 128

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Timer for highlighting limit reached
        self.limit_reached_timer = None

        # Initialize the UI
        self.initUI()

    def initUI(self):
        """Initialize the RibsTooltipEditor UI."""
        # Set window title and basic layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Instantiate RibsPlainTextEditor for tooltip input
        self.tooltip_input = self.RibsPlainTextEditor(self, max_chars=self.max_chars)
        self.tooltip_input.setFixedHeight(100)  # Approximately 5 line rows

        # Add to layout to make it visible and ready for input
        self.layout.addWidget(self.tooltip_input)

        # Instantiate character counter label
        self.tooltip_counter_label = RibsLabel(f"0/{self.max_chars}", "display", self)

        # Add counter label to layout
        self.layout.addWidget(self.tooltip_counter_label, alignment=Qt.AlignLeft)

        # Connect text changed signal to update counter and enforce limit
        self.tooltip_input.textChanged.connect(self._update_character_counter)
        # Connect to update save button clickability
        self.tooltip_input.textChanged.connect(self._on_text_changed)

        # Instantiate save button at the bottom and center it
        self.ribs_tooltip_editor_save_btn = RibsButton("Save", self, clickable=False)
        # Connect save button to emit signal with data
        self.ribs_tooltip_editor_save_btn.clicked.connect(self._on_save_clicked)

        # Add controlled spacing before save button
        self.spacing_pixels = 10  # Variable to adjust spacing in pixels (0 = minimal spacing)
        self.layout.setSpacing(self.spacing_pixels)

        # Add save button at the bottom, centered
        self.layout.addWidget(self.ribs_tooltip_editor_save_btn, alignment=Qt.AlignCenter)

    class RibsPlainTextEditor(QPlainTextEdit):
        def __init__(self, parent=None, max_chars=128):
            """
            Initialize the RibsPlainTextEditor widget using QPlainTextEdit.

            Args:
                parent: Parent widget
                max_chars: Maximum number of characters (default: 128)
            """
            super().__init__(parent)

            # Store parent
            self.parent_editor = parent

            # Get theme colors
            theme = Theme()
            self.colors = theme.get_colors()

            # Set max characters
            self.max_chars = max_chars

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

        def keyPressEvent(self, event):
            """
            Override keyPressEvent to enforce character limit.
            Prevent input when max characters reached, allow navigation and deletion.
            """
            if self.max_chars and len(self.toPlainText()) >= self.max_chars:
                # Allow control keys, navigation, and deletion
                if event.key() in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right,
                                   Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp,
                                   Qt.Key_PageDown, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab) or \
                   event.modifiers() & Qt.ControlModifier:  # allow ctrl+a, ctrl+v, etc.
                    pass  # allow
                else:
                    self.parent_editor._highlight_limit_reached()
                    event.ignore()
                    return
            super().keyPressEvent(event)

        def get_character_count(self):
            """
            Return the number of characters currently typed in the RibsPlainTextEditor.

            Returns:
                int: The total character count in the text editor
            """
            return len(self.toPlainText())

    def _update_character_counter(self):
        """
        Update the character counter label with current character count and enforce max chars.
        Called whenever text changes in tooltip_input.
        """
        text = self.tooltip_input.toPlainText()
        count = len(text)
        if count > self.max_chars:
            # Truncate to max chars
            self._highlight_limit_reached()
            text = text[:self.max_chars]
            self.tooltip_input.setPlainText(text)
            count = self.max_chars
        self.tooltip_counter_label.widget.setText(f"{count}/{self.max_chars}")

    def _highlight_limit_reached(self):
        """
        Highlight the counter label as error (red and bold) for 3 seconds when limit reached.
        """
        if self.limit_reached_timer:
            self.limit_reached_timer.stop()

        colors = Theme().get_colors()
        error_color = colors.get("error", "#FF0000")

        self.tooltip_counter_label.widget.setStyleSheet(f"color: {error_color}; font-weight: bold;")

        self.limit_reached_timer = QTimer()
        self.limit_reached_timer.setSingleShot(True)
        self.limit_reached_timer.timeout.connect(self._revert_label_style)
        self.limit_reached_timer.start(3000)

    def _revert_label_style(self):
        """
        Revert the counter label style back to normal.
        """
        self.tooltip_counter_label.widget.setStyleSheet("")
        self.limit_reached_timer = None

    def _on_text_changed(self):
        """
        Update the save button clickability based on whether text is present.
        Called whenever text changes in tooltip_input.
        """
        text = self.tooltip_input.toPlainText().strip()
        self.ribs_tooltip_editor_save_btn.set_clickable(bool(text))

    def _on_save_clicked(self):
        """
        Handle save button click to emit the save_data_signal with stripped text.
        Called when ribs_tooltip_editor_save_btn is clicked.
        """
        text = self.tooltip_input.toPlainText().strip()
        self.save_data_signal.emit(text)
        # Close the tooltip editor window after saving
        self.close()
