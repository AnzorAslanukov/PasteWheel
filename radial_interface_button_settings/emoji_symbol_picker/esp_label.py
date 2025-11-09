from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget, QVBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt
from theme import Theme


class EspLabel(QWidget):
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
        size=None,
        bordered=True
    ):
        """
        Initialize the EspLabel. A specialized label for EmojiSymbolPicker components.

        This label handles the same parameters as RibsLabel but operates differently by
        providing enhanced emoji/symbol text rendering specific to emoji selection contexts.

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
            size: List [width, height] to set fixed size, or None for content-based sizing (default: None)
            bordered: Boolean indicating if input-type labels should have border (default: True)
        """
        super().__init__(parent)

        # Store label type, padding, margin, clickable state, tooltips, alignments, and bordered state
        self.label_type = label_type
        self.is_input_type = (label_type == "input")
        self.padding = padding
        self.margin = margin
        self.clickable = clickable
        self.bordered = bordered
        self.display_alignment = display_alignment.lower()
        self.display_tooltip = display_tooltip
        self.input_clickable_tooltip = input_clickable_tooltip
        self.input_unclickable_tooltip = input_unclickable_tooltip

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
            # Process text to style emojis and symbols specifically for emoji picker
            styled_text = self._process_text_for_styling(text)
            self.widget = QLabel(styled_text, self)

        # Set input alignment for input-type labels
        if self.is_input_type and isinstance(self.widget, QLineEdit):
            if input_alignment.lower() == "left":
                self.widget.setAlignment(Qt.AlignLeft)
            elif input_alignment.lower() == "center":
                self.widget.setAlignment(Qt.AlignCenter)
            elif input_alignment.lower() == "right":
                self.widget.setAlignment(Qt.AlignRight)

        # Set display alignment for display-type labels
        elif not self.is_input_type and isinstance(self.widget, QLabel):
            self._set_display_alignment()

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
        """Apply theme-based styling to the label, optimized for emoji picker context."""
        # Get appropriate colors from theme
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")
        border_color = self.colors.get("border", "#CCCCCC")

        # Set border style based on bordered parameter
        if self.bordered:
            border_style = f"border: 1px solid {border_color};"
        else:
            border_style = "border: none;"

        # Apply stylesheet - adjusted for compact emoji picker display
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {background_color};
                color: {text_color};
                {border_style}
                padding: {self.padding}px;
                margin: {self.margin}px;
                font-size: 14px;  /* Slightly larger for emoji visibility */
            }}
            QLineEdit {{
                background-color: {background_color};
                color: {text_color};
                {border_style}
                padding: {self.padding}px;
                margin: {self.margin}px;
                font-size: 14px;
            }}
        """)

        # Set opacity using QGraphicsOpacityEffect for emoji picker visual feedback
        opacity_effect = QGraphicsOpacityEffect()
        if not self.clickable and self.is_input_type:
            opacity_effect.setOpacity(0.6)  # Different opacity for emoji picker context
        else:
            opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(opacity_effect)

    def enterEvent(self, event):
        """Handle mouse enter event - customized for emoji picker interaction with context-specific cursor behavior."""
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
            # For display labels, use standard arrow cursor (no pointing hand)
            self.setCursor(Qt.ArrowCursor)
            if self.display_tooltip:
                self.setToolTip(self.display_tooltip)
            else:
                self.setToolTip("")
        else:
            self.setCursor(Qt.ArrowCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event - restore cursor with emoji picker specific behavior."""
        if self.clickable and not self.is_input_type:
            self.setCursor(Qt.ArrowCursor)
        elif self.clickable and self.is_input_type:
            self.setCursor(Qt.IBeamCursor)
        else:
            self.setCursor(Qt.ForbiddenCursor)
        super().leaveEvent(event)

    def setAlignment(self, alignment):
        """Set alignment for QLabel widgets."""
        if isinstance(self.widget, QLabel):
            self.widget.setAlignment(alignment)

    def _process_text_for_styling(self, text):
        """
        Process text to apply special styling for emojis and symbols in emoji picker context.

        Args:
            text: The original text string

        Returns:
            Processed text with HTML styling for emoji characters
        """
        # Check if text contains emoji-like characters (basic unicode ranges)
        has_emoji = any(0x1F600 <= ord(c) <= 0x1F9FF or  # Emoticons, Misc Symbols and Pictographs
                        0x2600 <= ord(c) <= 0x26FF for c in text)  # Misc symbols

        if has_emoji:
            # Style emojis larger for better visibility in picker
            styled_parts = []
            for c in text:
                if 0x1F600 <= ord(c) <= 0x1F9FF or 0x2600 <= ord(c) <= 0x26FF:
                    styled_parts.append(f'<span style="font-size: 20px;">{c}</span>')
                else:
                    styled_parts.append(c)
            return f'<html><body>{"".join(styled_parts)}</body></html>'
        else:
            # No emoji characters, return original text
            return text

    def _set_display_alignment(self):
        """Set the alignment for display-type labels based on display_alignment parameter."""
        if isinstance(self.widget, QLabel):
            if self.display_alignment == "left":
                self.widget.setAlignment(Qt.AlignLeft)
            elif self.display_alignment == "center":
                self.widget.setAlignment(Qt.AlignCenter)
            elif self.display_alignment == "right":
                self.widget.setAlignment(Qt.AlignRight)

    def set_clickable(self, clickable):
        """Set the clickable state and update visual feedback for emoji picker."""
        self.clickable = clickable
        if self.is_input_type and isinstance(self.widget, QLineEdit):
            self.widget.setEnabled(clickable)
        # Reapply styling to update visual appearance
        self._apply_style()
