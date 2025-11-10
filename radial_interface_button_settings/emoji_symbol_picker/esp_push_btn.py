from PyQt5.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt
from theme import Theme


class EspPushBtn(QPushButton):
    def __init__(self, label="", parent=None, checked=False, clickable=True, display_tooltip=""):
        """
        Initialize the EspPushBtn.

        Args:
            label: Text to display on the button (default: "")
            parent: Parent widget
            checked: Boolean indicating if button is selected (default: False)
            clickable: Boolean indicating if button is clickable (default: True)
                When False, button will not be clickable and shows forbidden cursor on hover
            display_tooltip: Tooltip text shown on hover (default: "")
        """
        super().__init__(label, parent)

        # Store parameters
        self.checked = checked
        self.clickable = clickable
        self.display_tooltip = display_tooltip

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Set tooltip if provided
        if self.display_tooltip:
            self.setToolTip(self.display_tooltip)

        # Set fixed size for the button
        self.setFixedSize(40, 40)

        # Initialize button styling
        self._apply_style()

        # Set cursor based on clickability
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)

    def _apply_style(self, hovered=False):
        """Apply theme-based styling to the button."""
        # Get colors based on checked state
        if self.checked:
            background_color = self.colors.get("checked_button", "#4CAF50")  # Green for checked
            text_color = "#FFFFFF"  # White text on green background
            border_color = self.colors.get("accent", "#2E7D32")  # Darker green border
        else:
            background_color = self.colors.get("button", "#F0F0F0")
            text_color = self.colors.get("text", "#000000")
            border_color = self.colors.get("border", "#CCCCCC")

        # Hover effect for clickable buttons
        if hovered and self.clickable and not self.checked:
            hover_color = self.colors.get("button_hover", "#E0E0E0")
            background_color = hover_color

        # Apply stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 0px 0px;
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                qproperty-alignment: AlignCenter;
            }}
        """)

        # Set opacity using QGraphicsOpacityEffect for non-clickable state
        opacity_effect = QGraphicsOpacityEffect()
        if not self.clickable:
            opacity_effect.setOpacity(0.5)
        else:
            opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(opacity_effect)

    def enterEvent(self, event):
        """Handle mouse enter event - apply hover effect and set appropriate cursor."""
        if self.clickable:
            self._apply_style(hovered=True)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore normal styling and cursor."""
        self._apply_style(hovered=False)
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Override mouse press to prevent clicking on non-clickable buttons."""
        if self.clickable:
            # Toggle checked state on click for clickable buttons
            self.checked = not self.checked
            self._apply_style()

            # If we have an emoji code, save the new state to emoji_data.json
            if hasattr(self, 'emoji_code'):
                from pastewheel_config import PasteWheelConfig
                config = PasteWheelConfig()
                config.update_emoji_state(self.emoji_code, checked=self.checked)

            super().mousePressEvent(event)
        # Non-clickable buttons ignore mouse presses
