from PyQt5.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt
from theme import Theme
from debug_logger import DebugLogger

# Set to True to enable debug logging to debug.txt
DEBUG = False


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
        if DEBUG:
            DebugLogger.log(f"RibsButton._apply_style called: label='{self.text()}' clickable={self.clickable} hovered={hovered}")
        background_color = self.colors.get("button", "#F0F0F0")
        text_color = self.colors.get("text", "#000000")
        border_color = self.colors.get("border", "#CCCCCC")

        if hovered and self.clickable:
            # Darken background on hover for clickable buttons
            hover_color = self.colors.get("button_hover", "#E0E0E0")
            background_color = hover_color

        # Apply stylesheet without opacity in CSS
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: {self.padding};
            }}
        """)

        # Set opacity using QGraphicsOpacityEffect.
        # IMPORTANT: the effect must be stored as an instance variable so that
        # Python keeps a reference to it.  setGraphicsEffect() transfers C++
        # ownership to the widget; if the Python wrapper is a local variable it
        # goes out of scope immediately and Python's GC tries to delete the C++
        # object that Qt already owns -> double-free / use-after-free hard crash.
        if not hasattr(self, '_opacity_effect') or self._opacity_effect is None:
            self._opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self._opacity_effect)
            if DEBUG:
                DebugLogger.log(f"RibsButton: created new _opacity_effect for '{self.text()}'")

        self._opacity_effect.setOpacity(0.5 if not self.clickable else 1.0)

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

    def set_clickable(self, clickable):
        """
        Dynamically set the clickability of the button.

        Args:
            clickable: Boolean indicating if button should be clickable
        """
        if DEBUG:
            DebugLogger.log(f"RibsButton.set_clickable: '{self.text()}' -> {clickable}")
        self.clickable = clickable
        self._apply_style()

        # Update cursor based on new clickability state
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
