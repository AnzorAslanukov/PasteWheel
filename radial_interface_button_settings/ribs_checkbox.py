from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt
from theme import Theme


class RibsCheckbox(QCheckBox):
    def __init__(self, text="", checked=False, parent=None):
        """
        Initialize the RibsCheckbox.

        Args:
            text: The text to display next to the checkbox
            checked: Boolean indicating if checkbox should be initially checked
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set initial checked state
        self.setChecked(checked)

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Apply styling
        self._apply_style()

    def _apply_style(self):
        """Apply theme-based styling to the checkbox."""
        # Get appropriate colors from theme
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")

        # Apply stylesheet
        self.setStyleSheet(f"""
            QCheckBox {{
                background-color: {background_color};
                color: {text_color};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {self.colors.get("button", "#F0F0F0")};
                border: 1px solid {self.colors.get("border", "#CCCCCC")};
                border-radius: 2px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors.get("accent", "#007BFF")};
                border-color: {self.colors.get("accent", "#007BFF")};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors.get("accent", "#007BFF")};
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter event - change cursor to pointing hand."""
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore cursor to arrow."""
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
