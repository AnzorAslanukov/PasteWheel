from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from theme import Theme


class RibsLabel(QWidget):
    def __init__(
        self,
        text="",
        label_type="display",
        parent=None,
        padding=4,
        margin=0,
        clickable=True,
        display_tooltip="",
        input_clickable_tooltip="",
        input_unclickable_tooltip="",
        max_length=256,
        input_alignment="left"
    ):
        """
        Initialize the RibsLabel.

        Args:
            text: The text to display
            label_type: "display" or "input" - affects cursor behavior
            parent: Parent widget
            padding: Numeric value for padding in pixels (applied to all sides equally)
            margin: Numeric value for margin in pixels (applied to all sides equally)
            clickable: Boolean indicating if input-type labels should be clickable (default: True)
            display_tooltip: Tooltip text shown on hover for display-type labels when clickable=True
            input_clickable_tooltip: Tooltip text shown on hover for input-type labels when clickable=True
            input_unclickable_tooltip: Tooltip text shown on hover for input-type labels when clickable=False
            max_length: Maximum number of characters allowed in input-type labels (default: 256)
            input_alignment: Text alignment for input-type labels ("left", "center", "right"; default: "left")
        """
        super().__init__(parent)

        # Store label type, padding, margin, clickable state, and tooltips
        self.label_type = label_type
        self.is_input_type = (label_type == "input")
        self.padding = padding
        self.margin = margin
        self.clickable = clickable
        self.display_tooltip = display_tooltip
        self.input_clickable_tooltip = input_clickable_tooltip
        self.input_unclickable_tooltip = input_unclickable_tooltip

        # Create the appropriate widget based on type
        if self.is_input_type:
            self.widget = QLineEdit(text, self)
            self.widget.setMaxLength(max_length)  # Set maximum input length
            if not self.clickable:
                self.widget.setEnabled(False)
        else:
            self.widget = QLabel(text, self)

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Set input alignment for input-type labels
        if self.is_input_type and isinstance(self.widget, QLineEdit):
            if input_alignment.lower() == "left":
                self.widget.setAlignment(Qt.AlignLeft)
            elif input_alignment.lower() == "center":
                self.widget.setAlignment(Qt.AlignCenter)
            elif input_alignment.lower() == "right":
                self.widget.setAlignment(Qt.AlignRight)

        # Apply styling
        self._apply_style()

        # Set up the layout to contain the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)

        # Connect the child widget events to our handlers
        self.widget.enterEvent = lambda event: self.enterEvent(event)
        self.widget.leaveEvent = lambda event: self.leaveEvent(event)

    def _apply_style(self):
        """Apply theme-based styling to the label."""
        # Get appropriate colors from theme
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")

        # For input-type labels that are not clickable, use darkened colors
        if not self.clickable and self.is_input_type:
            background_color = self.colors.get("background", "#CCCCCC")  # Darken background
            text_color = self.colors.get("text", "#888888")  # Dim text color

        # Apply stylesheet
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {background_color};
                color: {text_color};
                padding: {self.padding}px;
                margin: {self.margin}px;
            }}
            QLineEdit {{
                background-color: {background_color};
                color: {text_color};
                border: 1px solid {self.colors.get("border", "#CCCCCC")};
                padding: {self.padding}px;
                margin: {self.margin}px;
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter event - change rib_btn_title_char_input_label based on label type and clickability, show tooltips."""
        if self.is_input_type and self.clickable:
            self.setCursor(Qt.IBeamCursor)
            if self.input_clickable_tooltip:
                self.setToolTip(self.input_clickable_tooltip)
            else:
                self.setToolTip("")
        elif self.is_input_type and not self.clickable:
            self.setCursor(Qt.ForbiddenCursor)
            if self.input_unclickable_tooltip:
                self.setToolTip(self.input_unclickable_tooltip)
            else:
                self.setToolTip("")
        elif not self.is_input_type and self.clickable:  # display type and clickable
            if self.display_tooltip:
                self.setToolTip(self.display_tooltip)
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setToolTip("")
                self.setCursor(Qt.ArrowCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore cursor based on clickability."""
        if self.clickable:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().leaveEvent(event)

    def setAlignment(self, alignment):
        """Set alignment for QLabel widgets."""
        if isinstance(self.widget, QLabel):
            self.widget.setAlignment(alignment)
