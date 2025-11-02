from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtCore import Qt
from theme import Theme


class RibsRadioBtn(QRadioButton):
    def __init__(self, text="", checked=False, parent=None, clickable=True):
        """
        Initialize the RibsRadioBtn.

        Args:
            text: The text to display next to the radio button
            checked: Boolean indicating initial checked state (default: False/off)
            parent: Parent widget
            clickable: Boolean indicating if radio button should be clickable (default: True)
        """
        super().__init__(text, parent)

        # Store clickable state
        self.clickable = clickable

        # Set initial checked state
        self.setChecked(checked)

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Handle cursor settings for non-clickable radio buttons
        if not self.clickable:
            self.setFocusPolicy(Qt.NoFocus)  # Prevent focus

        # Apply styling
        self._apply_style()

    def _apply_style(self):
        """Apply theme-based styling to the radio button."""
        # Get appropriate colors from theme
        text_color = self.colors.get("text", "#000000")

        # If not clickable, use darker background colors
        if not self.clickable:
            background_color = self.colors.get("background", "#CCCCCC")  # Use darker background
            indicator_bg = background_color  # Same darker color for indicator
            indicator_border = background_color  # Blend border with background
        else:
            indicator_bg = self.colors.get("button", "#F0F0F0")
            indicator_border = self.colors.get("border", "#CCCCCC")

        # Apply stylesheet with transparent background
        self.setStyleSheet(f"""
            QRadioButton {{
                background-color: transparent;
                color: {text_color};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background-color: {indicator_bg};
                border: 1px solid {indicator_border};
                border-radius: 8px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {self.colors.get("accent", "#007BFF")};
                border-color: {self.colors.get("accent", "#007BFF")};
            }}
            QRadioButton::indicator:hover {{
                border-color: {self.colors.get("accent", "#007BFF")};
            }}
            QRadioButton::indicator:checked::hover {{
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

    def mousePressEvent(self, event):
        """Override mouse press to prevent interaction with non-clickable radio buttons."""
        if self.clickable:
            super().mousePressEvent(event)
        # Non-clickable radio buttons ignore mouse presses

    def setChecked(self, checked):
        """Override setChecked to prevent changes for non-clickable radio buttons."""
        if not self.clickable:
            # Store the current state and prevent changes
            return
        super().setChecked(checked)
