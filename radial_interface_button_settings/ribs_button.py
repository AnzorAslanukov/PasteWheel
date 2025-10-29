from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from theme import Theme


class RibsButton(QPushButton):
    def __init__(self, label, parent=None, clickable=True):
        super().__init__(label, parent)

        # Store clickable state
        self.clickable = clickable

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Initialize button styling
        self._apply_style()

        # Set default cursor
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
            self.setEnabled(False)  # Make button unclickable

    def _apply_style(self, hovered=False):
        """Apply theme-based styling to the button."""
        background_color = self.colors.get("button", "#F0F0F0")
        text_color = self.colors.get("text", "#000000")
        border_color = self.colors.get("border", "#CCCCCC")

        # If not clickable, use darker background
        if not self.clickable:
            # Use an even darker color for disabled state
            background_color = self.colors.get("background", "#CCCCCC")  # Use background color as dark base
        elif hovered:
            # Darken background on hover for clickable buttons
            hover_color = self.colors.get("button_hover", "#E0E0E0")
            background_color = hover_color

        # Apply stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 8px 16px;
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter event - darken background and change cursor based on clickability."""
        if self.clickable:
            self._apply_style(hovered=True)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore normal background and cursor based on clickability."""
        self._apply_style(hovered=False)
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().leaveEvent(event)
