from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout
from PyQt5.QtCore import Qt
from theme import Theme


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
