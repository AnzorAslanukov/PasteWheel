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

        # Track all rendered button widgets so they can be refreshed later
        self.button_widgets = []

        # Maps button_id → RadialInterfaceButtonWidget for programmatic access
        self.button_widget_map = {}

        # Maps parent_id → list of child RadialInterfaceButtonWidget instances.
        # Used to show/hide children when an expand button is toggled.
        self.children_widgets_by_parent = {}

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
        Create and position RadialInterfaceButtonWidget instances.

        **Visibility rules (Rule 3):**
        Only Layer 1 buttons are visible when the interface first opens.
        Layer 2 and Layer 3 buttons are pre-rendered but hidden; they become
        visible only when their parent expand button is toggled on.

        **Positioning:**
        Layer 2 children are positioned as a group using the sibling count
        (children of the same parent), not the total Layer-2 count.  This
        ensures correct radial spacing regardless of how many other parents
        exist.  The same applies to Layer 3.
        """
        # Remove any previously rendered button widgets
        for widget in self.button_widgets:
            widget.deleteLater()
        self.button_widgets.clear()
        self.button_widget_map.clear()
        self.children_widgets_by_parent.clear()

        config = PasteWheelConfig()
        btn_size = RadialInterfaceButtonWidget.BUTTON_SIZE
        half = btn_size // 2

        # ── Layer 1 (always visible) ────────────────────────────────────
        total_l1 = len(self.layer1)
        for idx, button_data in enumerate(self.layer1):
            x, y = self._calculate_button_position(self.LAYER1_RADIUS, idx, total_l1)
            widget = RadialInterfaceButtonWidget(button_data, parent=self)
            widget.move(int(x) - half, int(y) - half)
            widget.show()
            self.button_widgets.append(widget)
            self.button_widget_map[button_data["id"]] = widget
            if button_data.get("button_type") == "exp":
                widget.expand_toggled.connect(self._on_expand_toggled)

        # ── Layer 2 (hidden initially; one group per Layer-1 expand parent) ─
        for l1_btn in self.layer1:
            if l1_btn.get("button_type") != "exp":
                continue
            parent_id = l1_btn["id"]
            children = config.get_child_buttons_by_parent(parent_id)
            total = len(children)
            child_widgets = []
            for idx, button_data in enumerate(children):
                x, y = self._calculate_button_position(self.LAYER2_RADIUS, idx, total)
                widget = RadialInterfaceButtonWidget(button_data, parent=self)
                widget.move(int(x) - half, int(y) - half)
                widget.hide()   # Rule 3: hidden until parent is toggled on
                self.button_widgets.append(widget)
                self.button_widget_map[button_data["id"]] = widget
                child_widgets.append(widget)
                if button_data.get("button_type") == "exp":
                    widget.expand_toggled.connect(self._on_expand_toggled)
            self.children_widgets_by_parent[parent_id] = child_widgets

        # ── Layer 3 (hidden initially; one group per Layer-2 expand parent) ─
        l2_expand_buttons = config.get_expand_buttons_by_layer(2)
        for l2_btn in l2_expand_buttons:
            parent_id = l2_btn["id"]
            children = config.get_child_buttons_by_parent(parent_id)
            total = len(children)
            child_widgets = []
            for idx, button_data in enumerate(children):
                x, y = self._calculate_button_position(self.LAYER3_RADIUS, idx, total)
                widget = RadialInterfaceButtonWidget(button_data, parent=self)
                widget.move(int(x) - half, int(y) - half)
                widget.hide()   # Rule 3: hidden until parent is toggled on
                self.button_widgets.append(widget)
                self.button_widget_map[button_data["id"]] = widget
                child_widgets.append(widget)
            self.children_widgets_by_parent[parent_id] = child_widgets

    # ------------------------------------------------------------------
    # Expand-button toggle logic (Rules 4 & 5)
    # ------------------------------------------------------------------

    def _on_expand_toggled(self, button_id: str, is_on: bool):
        """
        React to an expand button being toggled on or off.

        **Rule 4** — When turned ON, this button's direct children are shown.
                     When turned OFF, all descendants are hidden.

        **Rule 5** — When turned ON, every *other* expand button in the same
                     layer is turned off (and its descendants hidden).

        Args:
            button_id: ID of the expand button that was toggled.
            is_on:     New toggle state (True = ON, False = OFF).
        """
        config = PasteWheelConfig()
        button_data = config.get_button(button_id)
        if not button_data:
            return

        layer = button_data.get("layer", 1)

        if is_on:
            # Rule 5: turn off every other expand button in the same layer
            for other_btn in config.get_expand_buttons_by_layer(layer):
                if other_btn["id"] != button_id:
                    self._turn_off_expand_button(other_btn["id"])

            # Rule 4: show this button's direct children
            for child_widget in self.children_widgets_by_parent.get(button_id, []):
                child_widget.show()
        else:
            # Rule 4: hide all descendants when turned off
            self._hide_children_recursive(button_id)

    def _turn_off_expand_button(self, button_id: str):
        """
        Programmatically turn off an expand button and hide all its descendants.

        Uses :meth:`RadialInterfaceButtonWidget.set_toggled` (which does *not*
        emit ``expand_toggled``) to avoid re-entrant signal loops.

        Args:
            button_id: ID of the expand button to turn off.
        """
        widget = self.button_widget_map.get(button_id)
        if widget is not None:
            widget.set_toggled(False)
        self._hide_children_recursive(button_id)

    def _hide_children_recursive(self, parent_id: str):
        """
        Hide all children of *parent_id*.

        For any child that is itself an expand button and currently toggled on,
        recursively turn it off and hide its own children first.

        Args:
            parent_id: ID of the parent whose children should be hidden.
        """
        for child_widget in self.children_widgets_by_parent.get(parent_id, []):
            child_widget.hide()
            if child_widget.button_type == "exp" and child_widget.is_toggled:
                child_widget.set_toggled(False)
                self._hide_children_recursive(child_widget.button_id)

    # ------------------------------------------------------------------
    # UI initialisation
    # ------------------------------------------------------------------

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
        button_padding = 10
        self.close_btn.move(button_padding, self.height - 60)

        # Create keyboard button in upper-left corner
        self.keyboard_btn = RadialInterfaceControlButton(
            icon_path="assets/swap_alt_plus_apostrophe.svg",
            tooltip="Open PasteWheel with ALT+`",
            parent=self
        )
        self.keyboard_btn.move(button_padding, button_padding)

        # Create mouse button in upper-left corner (same position as keyboard_btn)
        self.mouse_btn = RadialInterfaceControlButton(
            icon_path="assets/swap_middle_mouse_button.svg",
            tooltip="Open PasteWheel with middle mouse button",
            parent=self
        )
        self.mouse_btn.move(button_padding, button_padding)
        self.mouse_btn.hide()

        # Create settings button in upper-right corner
        self.settings_btn = RadialInterfaceControlButton(
            icon_path="assets/settings_icon.svg",
            tooltip="Open PasteWheel settings",
            parent=self
        )
        button_size = 40
        self.settings_btn.move(self.width - button_size - button_padding, button_padding)

        # Create add-new-buttons button in centre of window
        self.add_new_btns = RadialInterfaceControlButton(
            icon_path="assets/add_first_button.svg",
            tooltip="Add your first clipboard button",
            parent=self
        )
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

        # Connect control button clicks
        self.keyboard_btn.clicked.connect(self.on_keyboard_btn_clicked)
        self.mouse_btn.clicked.connect(self.on_mouse_btn_clicked)
        self.add_new_btns.clicked.connect(self.on_add_new_btns_clicked)
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
        config = PasteWheelConfig()
        config.set_input_mode("keyboard")

    def on_mouse_btn_clicked(self):
        """Handle mouse button click - show keyboard button."""
        self.mouse_btn.hide()
        self.keyboard_btn.show()
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
            # Re-render button widgets whenever a button is saved or deleted
            # so the radial interface always reflects the latest config data.
            self.settings_window.buttons_changed.connect(self._on_buttons_changed)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _on_buttons_changed(self):
        """
        Re-render all radial interface button widgets from the current config.

        Called whenever the settings window saves or deletes a button so that
        the on-screen widgets always reflect the latest ``pastewheel_config.json``
        data (correct ``button_clipboard`` lists, labels, types, etc.).

        Steps:
          1. Reload ``self.layer1/2/3`` from config.
          2. Destroy all existing button widgets and create fresh ones.
          3. Sync the "add first button" centre widget visibility.
        """
        self._load_buttons_from_config()
        self._render_button_widgets()

        config = PasteWheelConfig()
        if config.has_any_buttons():
            self.add_new_btns.hide()
        else:
            self.add_new_btns.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen_color_hex = self.colors.get("foreground", "#000000")
        pen_color = QColor(pen_color_hex)
        pen = QPen(pen_color)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)

        center_x = self.width / 2
        center_y = self.height / 2

        # Circle 1: 100px diameter (50px radius)
        painter.drawEllipse(int(center_x - 50), int(center_y - 50), 100, 100)

        # Circle 2: 200px diameter (100px radius)
        painter.drawEllipse(int(center_x - 100), int(center_y - 100), 200, 200)

        # Circle 3: 300px diameter (150px radius)
        painter.drawEllipse(int(center_x - 150), int(center_y - 150), 300, 300)