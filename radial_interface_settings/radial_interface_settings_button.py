from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from theme import Theme


class RadialInterfaceSettingsButton(QPushButton):
    def __init__(self, label, parent=None):
        super().__init__(label, parent)
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        # Store original font size for click animation
        self.original_font_size = self.font().pointSize()
        self.shrink_timer = None
        
        # Initialize button styling
        self._apply_style()
        
        # Set cursor to pointing hand by default
        self.setCursor(Qt.PointingHandCursor)
    
    def _apply_style(self, hovered=False):
        """Apply theme-based styling to the button."""
        background_color = self.colors.get("button", "#F0F0F0")
        text_color = self.colors.get("text", "#000000")
        border_color = self.colors.get("border", "#CCCCCC")
        
        # Darken background on hover
        if hovered:
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
                font-size: 12pt;
            }}
            QPushButton:pressed {{
                background-color: {self.colors.get('button_hover', '#E0E0E0')};
            }}
        """)
    
    def enterEvent(self, event):
        """Handle mouse enter event - darken background and change cursor."""
        self._apply_style(hovered=True)
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event - restore normal background."""
        self._apply_style(hovered=False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press event - shrink text to 75%."""
        if event.button() == Qt.LeftButton:
            # Shrink font size to 75%
            current_font = self.font()
            new_size = int(self.original_font_size * 0.75)
            current_font.setPointSize(new_size)
            self.setFont(current_font)
            
            # Start timer to restore font size after 100ms
            self.shrink_timer = QTimer()
            self.shrink_timer.timeout.connect(self._restore_font_size)
            self.shrink_timer.start(100)
        
        super().mousePressEvent(event)
    
    def _restore_font_size(self):
        """Restore font size to original after click animation."""
        if self.shrink_timer:
            self.shrink_timer.stop()
            self.shrink_timer = None
        
        current_font = self.font()
        current_font.setPointSize(self.original_font_size)
        self.setFont(current_font)
