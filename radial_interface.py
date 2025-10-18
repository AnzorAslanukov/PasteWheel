from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
from radial_interface_control_button import RadialInterfaceControlButton
from radial_interface_settings.radial_interface_settings import RadialInterfaceSettings
from theme import Theme


class RadialInterface(QWidget):
    def __init__(self, width=400, height=400):
        super().__init__()
        self.width = width
        self.height = height
        self.settings_window = None
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Radial Interface')
        self.setGeometry(100, 100, self.width, self.height)
        
        # Apply theme background color
        background_color = self.colors.get("background", "#FFFFFF")
        self.setStyleSheet(f"background-color: {background_color};")
        
        # Create close button in lower-left corner
        self.close_btn = RadialInterfaceControlButton(
            icon_path="assets/close_pastewheel.svg",
            tooltip="Shutdown PasteWheel",
            parent=self
        )
        # Position button in lower-left corner with some padding
        button_padding = 10
        self.close_btn.move(button_padding, self.height - 60)
        
        # Create keyboard button in upper-left corner
        self.keyboard_btn = RadialInterfaceControlButton(
            icon_path="assets/swap_alt_plus_apostrophe.svg",
            tooltip="Open PasteWheel with ALT+`",
            parent=self
        )
        # Position button in upper-left corner with some padding
        self.keyboard_btn.move(button_padding, button_padding)
        
        # Create mouse button in upper-left corner (same position as keyboard_btn)
        self.mouse_btn = RadialInterfaceControlButton(
            icon_path="assets/swap_middle_mouse_button.svg",
            tooltip="Open PasteWheel with middle mouse button",
            parent=self
        )
        # Position button in upper-left corner with some padding (same as keyboard_btn)
        self.mouse_btn.move(button_padding, button_padding)
        # Initially hide mouse button
        self.mouse_btn.hide()
        
        # Create settings button in upper-right corner
        self.settings_btn = RadialInterfaceControlButton(
            icon_path="assets/settings_icon.svg",
            tooltip="Open PasteWheel settings",
            parent=self
        )
        # Position button in upper-right corner with some padding
        button_size = 40
        self.settings_btn.move(self.width - button_size - button_padding, button_padding)
        
        # Create add new buttons button in center of window
        self.add_new_btns = RadialInterfaceControlButton(
            icon_path="assets/add_first_button.svg",
            tooltip="Add your first clipboard button",
            parent=self
        )
        # Position button in center of window
        center_x = (self.width // 2) - (button_size // 2)
        center_y = (self.height // 2) - (button_size // 2)
        self.add_new_btns.move(center_x, center_y)
        
        # Connect button clicks to toggle visibility
        self.keyboard_btn.clicked.connect(self.on_keyboard_btn_clicked)
        self.mouse_btn.clicked.connect(self.on_mouse_btn_clicked)
        
        # Connect settings button to open settings window
        self.settings_btn.clicked.connect(self.on_settings_btn_clicked)

    def on_keyboard_btn_clicked(self):
        """Handle keyboard button click - show mouse button."""
        self.keyboard_btn.hide()
        self.mouse_btn.show()

    def on_mouse_btn_clicked(self):
        """Handle mouse button click - show keyboard button."""
        self.mouse_btn.hide()
        self.keyboard_btn.show()

    def on_settings_btn_clicked(self):
        """Handle settings button click - open settings window."""
        if self.settings_window is None:
            self.settings_window = RadialInterfaceSettings()
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set pen for drawing circles with solid lines using theme colors
        pen_color_hex = self.colors.get("foreground", "#000000")
        pen_color = QColor(pen_color_hex)
        pen = QPen(pen_color)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Calculate center of window
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Draw three concentric circles
        # Circle 1: 100px diameter (50px radius)
        painter.drawEllipse(int(center_x - 50), int(center_y - 50), 100, 100)
        
        # Circle 2: 200px diameter (100px radius)
        painter.drawEllipse(int(center_x - 100), int(center_y - 100), 200, 200)
        
        # Circle 3: 300px diameter (150px radius)
        painter.drawEllipse(int(center_x - 150), int(center_y - 150), 300, 300)
