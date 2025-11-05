from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QTimer
from theme import Theme


class EspBtn(QPushButton):
    """
    A themed button class for emoji symbol picker buttons.
    Inherits styling from the Theme class.
    """

    # Class attributes for fixed button properties - can be modified for all instances
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 30
    FONT_SIZE = 12

    def __init__(self, text="", parent=None, checked=False):
        """
        Initialize the EspBtn (Emoji Symbol Picker Button).

        Args:
            text: The button text (emoji/symbol character)
            parent: Parent widget (optional)
            checked: Whether the button should be in checked state (default: False)
        """
        super().__init__(text, parent)
        self.checked = checked
        self.original_font_size = self.FONT_SIZE  # Use class attribute for font size

        # Set fixed size for all EspBtn instances using class attributes
        self.setFixedSize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

        # Get theme colors
        self.theme = Theme()
        self.colors = self.theme.get_colors()

        # Connect clicked signal to toggle checked state
        self.clicked.connect(self.toggle_checked)

        # Apply theme-aware styling
        self.apply_styling()

    def apply_styling(self):
        """Apply theme-based styling to the EspBtn."""
        # Check if button is in checked state
        if self.checked:
            background_color = self.colors.get("checked_button", "#4CAF50")
            text_color = "#FFFFFF"  # White text for better contrast on green
        else:
            background_color = self.colors.get("button", "#F0F0F0")
            text_color = self.colors.get("text", "#000000")

        border_color = self.colors.get("border", "#CCCCCC")
        hover_color = self.colors.get("button_hover", "#E0E0E0")
        accent_color = self.colors.get("accent", "#007BFF")
        checked_button_color = self.colors.get("checked_button", "#4CAF50")

        # Apply stylesheet with theme colors
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                font-size: {self.original_font_size}px;
                font-weight: bold;
                padding: 1px 2px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {accent_color};
            }}
            QPushButton:focus {{
                outline: none;
                border-color: {accent_color};
            }}
        """)

    def set_selected(self, selected=False):
        """
        Set the button's selected state for visual feedback.

        Args:
            selected: Whether the button is in selected state
        """
        if selected:
            accent_color = self.colors.get("accent", "#007BFF")
            self.setStyleSheet(self.styleSheet() + f"""
                QPushButton {{
                    background-color: {accent_color};
                    color: white;
                    border-color: {accent_color};
                }}
            """)
        else:
            self.apply_styling()  # Reset to default styling

    def set_hover_style(self, hovering=False):
        """
        Apply or remove hover style programmatically.

        Args:
            hovering: Whether to apply hover styling
        """
        if hovering:
            hover_color = self.colors.get("button_hover", "#E0E0E0")
            accent_color = self.colors.get("accent", "#007BFF")
            self.setStyleSheet(self.styleSheet() + f"""
                QPushButton {{
                    background-color: {hover_color};
                    border-color: {accent_color};
                }}
            """)
        else:
            self.apply_styling()  # Reset to default styling

    def mousePressEvent(self, event):
        """
        Override mouse press event to shrink text size to 50% during press.

        Args:
            event: QMouseEvent
        """
        if event.button() == Qt.LeftButton:
            # Shrink text to 50% of original size
            self.setStyleSheet(self.styleSheet().replace(
                f"font-size: {self.original_font_size}px",
                f"font-size: {self.original_font_size // 2}px"
            ))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Override mouse release event to restore text size.

        Args:
            event: QMouseEvent
        """
        if event.button() == Qt.LeftButton:
            # Restore original text size
            self.setStyleSheet(self.styleSheet().replace(
                f"font-size: {self.original_font_size // 2}px",
                f"font-size: {self.original_font_size}px"
            ))
        super().mouseReleaseEvent(event)

    def toggle_checked(self):
        """
        Toggle the checked state of the button and update styling.
        """
        self.checked = not self.checked
        self.apply_styling()
