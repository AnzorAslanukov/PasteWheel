from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget, QVBoxLayout, QGraphicsOpacityEffect
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
        input_alignment="left",
        display_alignment="left",
        font_size=None,
        size=None
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
            display_alignment: Text alignment for display-type labels ("left", "center", "right"; default: "left")
            font_size: Font size in pixels for the label, or None to use system default (default: None)
            size: List [width, height] to set fixed size, or None for content-based sizing (default: None)
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
        self.display_alignment = display_alignment
        self.font_size = font_size

        # Get theme colors first (needed for text processing)
        theme = Theme()
        self.colors = theme.get_colors()

        # Create the appropriate widget based on type
        if self.is_input_type:
            self.widget = QLineEdit(text, self)
            self.widget.setMaxLength(max_length)  # Set maximum input length
            if not self.clickable:
                self.widget.setEnabled(False)
        else:
            # Process text to style "ⓘ" character
            styled_text = self._process_text_for_styling(text)
            self.widget = QLabel(styled_text, self)
            # Set display alignment for display-type labels
            if display_alignment.lower() == "left":
                self.widget.setAlignment(Qt.AlignLeft)
            elif display_alignment.lower() == "center":
                self.widget.setAlignment(Qt.AlignCenter)
            elif display_alignment.lower() == "right":
                self.widget.setAlignment(Qt.AlignRight)

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

        # Set fixed size if specified
        if size is not None:
            if isinstance(size, list) and len(size) == 2:
                width, height = size
                self.setFixedSize(width, height)
            else:
                raise ValueError("size parameter must be a list of [width, height] or None")

        # Connect the child widget events to our handlers
        self.widget.enterEvent = lambda event: self.enterEvent(event)
        self.widget.leaveEvent = lambda event: self.leaveEvent(event)

    def _apply_style(self):
        """Apply theme-based styling to the label."""
        # Get appropriate colors from theme
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")

        # Build font-size style if specified
        font_size_style = f"font-size: {self.font_size}px;" if self.font_size is not None else ""

        # Apply stylesheet - remove color changes for unclickable state
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {background_color};
                color: {text_color};
                padding: {self.padding}px;
                margin: {self.margin}px;
                {font_size_style}
            }}
            QLineEdit {{
                background-color: {background_color};
                color: {text_color};
                border: 1px solid {self.colors.get("border", "#CCCCCC")};
                padding: {self.padding}px;
                margin: {self.margin}px;
                {font_size_style}
            }}
        """)

        # Set opacity using QGraphicsOpacityEffect
        opacity_effect = QGraphicsOpacityEffect()
        if not self.clickable:
            opacity_effect.setOpacity(0.5)
        else:
            opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(opacity_effect)

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

    def _process_text_for_styling(self, text):
        """
        Process text to apply special styling to the "ⓘ" character if present.

        Args:
            text: The original text string

        Returns:
            Processed text with HTML styling for the special character
        """
        # Check if "ⓘ" character exists in the text
        if "ⓘ" in text:
            # Get the circle_i color from theme
            circle_i_color = self.colors.get("circle_i", "#007AFF")

            # Replace "ⓘ" with styled version (bold and colored)
            styled_text = text.replace("ⓘ", f'<font color="{circle_i_color}"><b>ⓘ</b></font>')

            # Return as HTML-formatted text
            return f'<html><body>{styled_text}</body></html>'
        else:
            # No special character, return original text
            return text

    def set_clickable(self, clickable):
        """Set the clickable state and update visual feedback."""
        self.clickable = clickable
        if self.is_input_type and isinstance(self.widget, QLineEdit):
            self.widget.setEnabled(clickable)
        # Reapply styling to update visual appearance
        self._apply_style()
