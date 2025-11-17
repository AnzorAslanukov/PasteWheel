from PyQt5.QtWidgets import QCheckBox, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QEvent
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

        # Create opacity effect once (reused in _apply_style)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Apply styling
        self._apply_style()

        # Set initial cursor based on clickability
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)

    def _apply_style(self):
        """Apply theme-based styling to the checkbox."""
        # Get appropriate colors from theme
        text_color = self.colors.get("text", "#000000")

        # Apply stylesheet (use standard colors, let opacity handle disabled appearance)
        indicator_bg = self.colors.get("button", "#F0F0F0")
        indicator_border = self.colors.get("border", "#CCCCCC")

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

        # Update opacity based on clickability
        if not self.clickable:
            self.opacity_effect.setOpacity(0.5)
        else:
            self.opacity_effect.setOpacity(1.0)

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
        """Override mouse press to block clicks on non-clickable checkboxes."""
        if not self.clickable:
            # Consume the event without processing it
            event.ignore()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Override mouse release to block clicks on non-clickable checkboxes."""
        if not self.clickable:
            # Consume the event without processing it
            event.ignore()
            return
        super().mouseReleaseEvent(event)

    def hitButton(self, pos):
        """Override to prevent the checkbox from responding to clicks when not clickable."""
        if not self.clickable:
            return False
        return super().hitButton(pos)

    def nextCheckState(self):
        """Override to prevent state changes when not clickable."""
        if not self.clickable:
            return
        super().nextCheckState()

    def set_clickable(self, clickable):
        """
        Set the clickable state of the checkbox.

        Args:
            clickable: Boolean indicating if checkbox should be clickable
        """
        self.clickable = clickable
        
        # Update styling
        self._apply_style()

        # Update cursor based on new clickability state
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)