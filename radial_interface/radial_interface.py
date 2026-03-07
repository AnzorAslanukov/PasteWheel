from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
import math
from radial_interface.radial_interface_control_button import RadialInterfaceControlButton
from radial_interface.radial_interface_button_widget import RadialInterfaceButtonWidget
from radial_interface_settings.radial_interface_settings import RadialInterfaceSettings
from radial_interface_button_settings.radial_interface_button_settings import RadialInterfaceButtonSettings
from theme import Theme
from pastewheel_config import PasteWheelConfig


class RadialInterface(QWidget):
    # Layer capacity constraints.
    # Layer 1: 8 buttons total.
    # Layer 2: 16 child buttons per Layer-1 expand button; up to 8 parents → 128 total.
    # Layer 3: 24 child buttons per Layer-2 expand button; up to 128 parents → 3072 total.
    LAYER1_MAX_BUTTONS = 8
    LAYER2_MAX_BUTTONS = 128   # 8 parents × 16 children
    LAYER3_MAX_BUTTONS = 3072  # 128 parents × 24 children
    
    # Circle radii
    LAYER1_RADIUS = 50
    LAYER2_RADIUS = 100
    LAYER3_RADIUS = 150

    def __init__(self, width=400, height=400, layer1=None, layer2=None, layer3=None):
        super().__init__()
        self.width = width
        self.height = height
        self.settings_window = None
        self.button_settings_window = None
        
        # Initialize layers with validation
        self.layer1 = layer1 if layer1 is not None else []
        self.layer2 = layer2 if layer2 is not None else []
        self.layer3 = layer3 if layer3 is not None else []
        
        # Validate layer capacities
        self._validate_layers()
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        # Track rendered button widgets so they can be refreshed later
        self.button_widgets = []

        self.initUI()

    def _validate_layers(self):
        """Validate that layers don't exceed their capacity constraints."""
        if len(self.layer1) > self.LAYER1_MAX_BUTTONS:
            raise ValueError(f"Layer 1 can contain maximum {self.LAYER1_MAX_BUTTONS} buttons, got {len(self.layer1)}")
        if len(self.layer2) > self.LAYER2_MAX_BUTTONS:
            raise ValueError(f"Layer 2 can contain maximum {self.LAYER2_MAX_BUTTONS} buttons, got {len(self.layer2)}")
        if len(self.layer3) > self.LAYER3_MAX_BUTTONS:
            raise ValueError(f"Layer 3 can contain maximum {self.LAYER3_MAX_BUTTONS} buttons, got {len(self.layer3)}")
    
    def _calculate_button_position(self, layer_radius, button_index, total_buttons_in_layer):
        """
        Calculate the position of a button on a circular layer.
        
        Args:
            layer_radius: Radius of the circle (50, 100, or 150)
            button_index: Index of the button in the layer (0-based)
            total_buttons_in_layer: Total number of buttons in this layer
        
        Returns:
            Tuple of (x, y) coordinates for the button center
        """
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Calculate angle in degrees for equal spacing
        angle_degrees = (360 / total_buttons_in_layer) * button_index
        # Convert to radians
        angle_radians = math.radians(angle_degrees)
        
        # Calculate position on circle
        x = center_x + layer_radius * math.cos(angle_radians)
        y = center_y + layer_radius * math.sin(angle_radians)
        
        return (x, y)
    
    def get_layer_button_positions(self, layer_num):
        """
        Get all button positions for a specific layer.
        
        Args:
            layer_num: Layer number (1, 2, or 3)
        
        Returns:
            List of (x, y) tuples for each button in the layer
        """
        if layer_num == 1:
            layer = self.layer1
            radius = self.LAYER1_RADIUS
        elif layer_num == 2:
            layer = self.layer2
            radius = self.LAYER2_RADIUS
        elif layer_num == 3:
            layer = self.layer3
            radius = self.LAYER3_RADIUS
        else:
            raise ValueError("Layer number must be 1, 2, or 3")
        
        positions = []
        for i in range(len(layer)):
            pos = self._calculate_button_position(radius, i, len(layer))
            positions.append(pos)
        
        return positions

    def _load_buttons_from_config(self):
        """
        Read button data from PasteWheelConfig and populate self.layer1/2/3.
        Called during initUI so the layers reflect the saved configuration.
        """
        config = PasteWheelConfig()
        for layer_num, layer_list in [(1, self.layer1), (2, self.layer2), (3, self.layer3)]:
            layer_buttons = config.get_buttons_by_layer(layer_num)
            if layer_buttons:
                layer_list.clear()
                layer_list.extend(layer_buttons)
        self._validate_layers()

    def _render_button_widgets(self):
        """
        Create and position a RadialInterfaceButtonWidget for every button
        in layer1, layer2, and layer3.  Existing widgets are removed first.
        """
        # Remove any previously rendered button widgets
        for widget in self.button_widgets:
            widget.deleteLater()
        self.button_widgets.clear()

        layer_map = {
            1: (self.layer1, self.LAYER1_RADIUS),
            2: (self.layer2, self.LAYER2_RADIUS),
            3: (self.layer3, self.LAYER3_RADIUS),
        }

        btn_size = RadialInterfaceButtonWidget.BUTTON_SIZE
        half = btn_size // 2

        for layer_num, (layer_list, radius) in layer_map.items():
            total = len(layer_list)
            if total == 0:
                continue
            for idx, button_data in enumerate(layer_list):
                x, y = self._calculate_button_position(radius, idx, total)
                widget = RadialInterfaceButtonWidget(button_data, parent=self)
                # Centre the widget on the calculated position
                widget.move(int(x) - half, int(y) - half)
                widget.show()
                self.button_widgets.append(widget)

    def initUI(self):
        self.setWindowTitle('Radial Interface')
        self.setGeometry(100, 100, self.width, self.height)

        # Load button data from config into self.layer1/2/3
        self._load_buttons_from_config()

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

        # Hide the "add first button" widget when buttons already exist in config;
        # show it only when there are no buttons yet.
        config = PasteWheelConfig()
        if config.has_any_buttons():
            self.add_new_btns.hide()
        else:
            self.add_new_btns.show()

        # Render existing buttons as visual widgets on the radial rings
        self._render_button_widgets()

        # Connect button clicks to toggle visibility
        self.keyboard_btn.clicked.connect(self.on_keyboard_btn_clicked)
        self.mouse_btn.clicked.connect(self.on_mouse_btn_clicked)
        self.add_new_btns.clicked.connect(self.on_add_new_btns_clicked)

        # Connect settings button to open settings window
        self.settings_btn.clicked.connect(self.on_settings_btn_clicked)

        # Set initial button visibility based on saved input mode
        config = PasteWheelConfig()
        input_mode = config.get_input_mode()
        if input_mode == "mouse":
            self.keyboard_btn.show()
            self.mouse_btn.hide()
        else:  # default to keyboard mode
            self.keyboard_btn.hide()
            self.mouse_btn.show()

    def on_keyboard_btn_clicked(self):
        """Handle keyboard button click - show mouse button."""
        self.keyboard_btn.hide()
        self.mouse_btn.show()
        # Save input mode to configuration
        config = PasteWheelConfig()
        config.set_input_mode("keyboard")

    def on_mouse_btn_clicked(self):
        """Handle mouse button click - show keyboard button."""
        self.mouse_btn.hide()
        self.keyboard_btn.show()
        # Save input mode to configuration
        config = PasteWheelConfig()
        config.set_input_mode("mouse")

    def on_add_new_btns_clicked(self):
        """Handle add-new-buttons click — open button settings for the first layer-1 button."""
        if self.button_settings_window is None:
            self.button_settings_window = RadialInterfaceButtonSettings(
                button_id=None, layer=1, parent=self
            )
        self.button_settings_window.show()
        self.button_settings_window.raise_()
        self.button_settings_window.activateWindow()

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
