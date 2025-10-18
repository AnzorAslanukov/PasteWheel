from PyQt5.QtWidgets import QPushButton, QToolTip
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from theme import Theme


class RadialInterfaceControlButton(QPushButton):
    def __init__(self, icon_path, background_color="transparent", tooltip="", parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.background_color = background_color
        self.tooltip_text = tooltip
        self.button_size = 40
        self.is_hovered = False
        self.original_icon_size = None
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.restore_icon_size)
        
        # Set up button properties
        self.initUI()

    def initUI(self):
        """Initialize the button UI with circular shape and icon."""
        # Set button size
        self.setFixedSize(self.button_size, self.button_size)
        
        # Load and set icon
        icon = QIcon(self.icon_path)
        self.setIcon(icon)
        self.original_icon_size = QSize(self.button_size - 10, self.button_size - 10)
        self.setIconSize(self.original_icon_size)
        
        # Set tooltip if provided
        if self.tooltip_text:
            self.setToolTip(self.tooltip_text)
        
        # Make button circular with transparent background
        button_hover_color = self.colors.get("button_hover", "#E0E0E0")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: {self.button_size // 2}px;
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
                border-radius: {self.button_size // 2}px;
            }}
        """)
        
        # Set initial opacity effect for icon
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)  # 100% opacity by default
        self.setGraphicsEffect(self.opacity_effect)
        
        # Connect click signal
        self.clicked.connect(self.on_button_clicked)

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        self.is_hovered = True
        # Set opacity to 75% on hover
        self.opacity_effect.setOpacity(0.5)
        # Show tooltip if provided - positioned on upper right of mouse cursor
        if self.tooltip_text:
            global_pos = self.mapToGlobal(event.pos())
            tooltip_pos = QPoint(global_pos.x() + 15, global_pos.y() - 20)
            QToolTip.showText(tooltip_pos, self.tooltip_text, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        self.is_hovered = False
        # Set opacity back to 100%
        self.opacity_effect.setOpacity(1.0)
        # Hide tooltip when mouse leaves
        QToolTip.hideText()
        super().leaveEvent(event)

    def on_button_clicked(self):
        """Handle button click event."""
        # Shrink icon to 75% of original size
        shrink_factor = 0.75
        shrunk_size = QSize(
            int(self.original_icon_size.width() * shrink_factor),
            int(self.original_icon_size.height() * shrink_factor)
        )
        self.setIconSize(shrunk_size)
        
        # Restore icon size after 100ms
        self.click_timer.start(100)

    def restore_icon_size(self):
        """Restore icon to original size after click animation."""
        self.setIconSize(self.original_icon_size)
