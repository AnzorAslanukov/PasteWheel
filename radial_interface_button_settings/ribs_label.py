from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from theme import Theme


class RibsLabel(QLabel):
    def __init__(self, text="", label_type="display", parent=None):
        """
        Initialize the RibsLabel.

        Args:
            text: The text to display
            label_type: "display" or "input" - affects cursor behavior
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Store label type
        self.label_type = label_type
        self.is_input_type = (label_type == "input")

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Set default cursor
        self.setCursor(Qt.ArrowCursor)

        # Apply styling
        self._apply_style()

    def _apply_style(self):
        """Apply theme-based styling to the label."""
        # Get appropriate colors from theme
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")

        # Apply stylesheet
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {background_color};
                color: {text_color};
                padding: 4px;
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter event - change cursor based on label type."""
        if self.is_input_type:
            self.setCursor(Qt.IBeamCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore cursor to arrow."""
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
