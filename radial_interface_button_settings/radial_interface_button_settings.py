from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from theme import Theme


class RadialInterfaceButtonSettings(QWidget):
    def __init__(self, button_id=None, parent=None):
        """
        Initialize the RadialInterfaceButtonSettings window.
        
        Args:
            button_id: ID of the button to configure (optional)
            parent: Parent widget
        """
        super().__init__(parent, Qt.Window)
        self.button_id = button_id
        self.width = 400
        self.height = 400
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        self.initUI()
    
    def initUI(self):
        """Initialize the RadialInterfaceButtonSettings UI."""
        # Set window title
        if self.button_id:
            self.setWindowTitle(f'Button Settings - ID: {self.button_id}')
        else:
            self.setWindowTitle('Button Settings')
        
        # Position the window offset from parent to make it visible
        # If parent exists, offset the position
        if self.parent():
            parent_x = self.parent().x() if hasattr(self.parent(), 'x') else 100
            parent_y = self.parent().y() if hasattr(self.parent(), 'y') else 100
            offset_x = parent_x + 450  # Offset to the right
            offset_y = parent_y
        else:
            offset_x = 100
            offset_y = 100
        
        self.setGeometry(offset_x, offset_y, self.width, self.height)
        print(f"DEBUG: RadialInterfaceButtonSettings geometry set to: {offset_x}, {offset_y}, {self.width}, {self.height}")
        
        # Apply theme colors to the window background and text
        background_color = self.colors.get("background", "#FFFFFF")
        foreground_color = self.colors.get("foreground", "#000000")
        button_color = self.colors.get("button", "#F0F0F0")
        button_hover_color = self.colors.get("button_hover", "#E0E0E0")
        text_color = self.colors.get("text", "#000000")
        border_color = self.colors.get("border", "#CCCCCC")
        
        # Apply stylesheet with theme colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QLineEdit {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 5px;
            }}
        """)
        
        # Create main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
    
    def open_button_settings(self, button_id=None):
        """
        Open the RadialInterfaceButtonSettings window.
        
        Args:
            button_id: ID of the button to configure (optional)
        """
        # Update button_id if provided
        if button_id is not None:
            self.button_id = button_id
            # Update window title with new button_id
            if self.button_id:
                self.setWindowTitle(f'Button Settings - ID: {self.button_id}')
            else:
                self.setWindowTitle('Button Settings')
        
        # Show the window
        self.show()
        self.raise_()
        self.activateWindow()
