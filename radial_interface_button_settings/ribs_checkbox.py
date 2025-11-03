from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt
from theme import Theme


class RibsCheckbox(QCheckBox):
    def __init__(self, text="", checked=False, parent=None, clickable=True):
        """
        Initialize the RibsCheckbox.

        Args:
            text: The text to display next to the checkbox
            checked: Boolean indicating if checkbox should be initially checked
            parent: Parent widget
            clickable: Boolean indicating if checkbox should be clickable (default: True)
        """
        super().__init__(text, parent)

        # Store clickable state
        self.clickable = clickable

        # Set initial checked state
        self.setChecked(checked)

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Handle non-clickable checkboxes
        if not self.clickable:
            self.setEnabled(False)

        # Apply styling
        self._apply_style()

    def _apply_style(self):
        """Apply theme-based styling to the checkbox."""
        # Get appropriate colors from theme
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")

        # If not clickable, use darker background colors
        if not self.clickable:
            background_color = self.colors.get("background", "#CCCCCC")  # Use darker background
            indicator_bg = background_color  # Same darker color for indicator
            indicator_border = background_color  # Blend border with background
        else:
            indicator_bg = self.colors.get("button", "#F0F0F0")
            indicator_border = self.colors.get("border", "#CCCCCC")

        # Apply stylesheet
        self.setStyleSheet(f"""
            QCheckBox {{
                background-color: transparent;
                color: {text_color};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {indicator_bg};
                border: 1px solid {indicator_border};
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
        """Handle mouse enter event - change cursor based on clickability."""
        if self.clickable:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore cursor based on clickability."""
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().leaveEvent(event)
