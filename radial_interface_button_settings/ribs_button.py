from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from theme import Theme


class RibsButton(QPushButton):
    def __init__(self, label, parent=None, clickable=True, min_height=None, padding=None):
        """
        Initialize the RibsButton.

        Args:
            label: Text to display on the button
            parent: Parent widget
            clickable: Whether the button is clickable (default: True)
            min_height: Minimum height in pixels (optional)
            padding: CSS-like padding string, e.g. "8px 16px" (optional)
        """
        super().__init__(label, parent)

        # Store clickable state
        self.clickable = clickable

        # Store size parameters
        self.min_height = min_height
        self.padding = padding or "4px 16px"

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Initialize button styling
        self._apply_style()

        # Set button size if min_height specified
        if self.min_height:
            self.setMinimumHeight(self.min_height)

        # Set cursor based on clickability
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)

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
                padding: {self.padding};
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

    def mousePressEvent(self, event):
        """Override mouse press to prevent clicking on non-clickable buttons."""
        if self.clickable:
            super().mousePressEvent(event)
        # Non-clickable buttons ignore mouse presses
