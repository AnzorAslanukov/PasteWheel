from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from functools import partial
from theme import Theme
from pastewheel_config import PasteWheelConfig
from radial_interface_settings.radial_interface_settings_button import RadialInterfaceSettingsButton
from debug_logger import DebugLogger

# Set to True to enable debug logging to debug.txt
DEBUG = False

DELETE_ICON_PATH = "assets/delete_icon.svg"

# Maximum number of buttons allowed per layer
LAYER_MAX_BUTTONS = {1: 8, 2: 16, 3: 24}


class ButtonTab(QWidget):
    def __init__(self, parent=None, layer=None, enabled=True, settings_window=None, tooltip=None):
        """
        Initialize the Button tab.

        Args:
            parent: Parent widget
            layer: Layer number (1, 2, or 3) to identify the tab
            enabled: Boolean indicating whether tab should be visible and clickable (default: True)
            settings_window: Reference to parent RadialInterfaceSettings window
            tooltip: Optional tooltip string shown on the tab bar entry when hovering.
                     Pass None (default) or an empty string for no tooltip.
        """
        super().__init__(parent)
        self.layer = layer
        self.settings_window = settings_window
        self.tooltip = tooltip or ""

        # Get theme colors
        theme = Theme()
        colors = theme.get_colors()

        # Set color properties from theme
        self.color_background = colors.get("background", "#FFFFFF")
        self.color_foreground = colors.get("foreground", "#000000")
        self.color_button = colors.get("button", "#F0F0F0")
        self.color_button_hover = colors.get("button_hover", "#E0E0E0")
        self.color_text = colors.get("text", "#000000")
        self.color_text_secondary = colors.get("text_secondary", "#666666")
        self.color_border = colors.get("border", "#CCCCCC")
        self.color_accent = colors.get("accent", "#007BFF")

        self.is_enabled = enabled
        self.initUI()
        self.set_enabled(enabled)

    def initUI(self):
        """Initialize the Button tab UI."""
        # Outer layout holds a scroll area so many buttons don't overflow
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignTop)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_layout)

        # Scroll area for the button list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        # Inner container widget inside the scroll area
        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setAlignment(Qt.AlignTop)
        self.inner_layout.setSpacing(6)
        self.inner_layout.setContentsMargins(8, 8, 8, 8)

        scroll_area.setWidget(self.inner_widget)
        outer_layout.addWidget(scroll_area)

        # Populate with buttons from config
        self._populate()

    def _make_delete_icon(self):
        """
        Build a QIcon from the delete SVG asset.

        Returns:
            QIcon loaded from DELETE_ICON_PATH, or an empty QIcon if the file
            cannot be rendered.
        """
        renderer = QSvgRenderer(DELETE_ICON_PATH)
        if not renderer.isValid():
            return QIcon()
        size = QSize(24, 24)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        return QIcon(pixmap)

    def _populate(self):
        """
        Populate the tab with buttons based on the current configuration for this layer.

        Cases:
        - No buttons in this layer → show "Add first clipboard button" placeholder
        - 1 to (max-1) buttons    → show [Edit 80% | Delete 20%] row per button
                                     + "Add new button" at the bottom
        - Layer is full (max)     → show [Edit | Delete] rows only, no "Add new button"
        """
        config = PasteWheelConfig()
        layer_buttons = config.get_buttons_by_layer(self.layer) or []
        max_buttons = LAYER_MAX_BUTTONS.get(self.layer, 8)

        if not layer_buttons:
            # No buttons saved yet — show the original placeholder
            add_button = RadialInterfaceSettingsButton(
                "Add first\nclipboard button", parent=self.inner_widget
            )
            add_button.clicked.connect(self.on_add_button_clicked)
            self.inner_layout.addWidget(add_button, alignment=Qt.AlignCenter)
        else:
            delete_icon = self._make_delete_icon()

            # Show an [Edit | Delete] row for each existing button
            for btn_data in layer_buttons:
                button_id = btn_data.get("id", "")
                label = btn_data.get("label", button_id)

                # Row container
                row_widget = QWidget(self.inner_widget)
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(4)

                # Edit button — 80% of row width
                edit_btn = RadialInterfaceSettingsButton(
                    f"Edit: {label}", parent=row_widget
                )
                edit_btn.clicked.connect(partial(self.on_edit_button_clicked, button_id))

                # Delete button — 20% of row width, SVG icon only
                delete_btn = QPushButton(row_widget)
                delete_btn.setIcon(delete_icon)
                delete_btn.setIconSize(QSize(20, 20))
                delete_btn.setToolTip("Delete this button")
                delete_btn.setCursor(Qt.PointingHandCursor)
                # Match the delete button height exactly to the edit button's natural height
                delete_btn.setFixedHeight(edit_btn.sizeHint().height())
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.color_button};
                        border: 1px solid {self.color_border};
                        border-radius: 4px;
                        padding: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: #e53935;
                        border-color: #b71c1c;
                    }}
                """)
                delete_btn.clicked.connect(partial(self.on_delete_button_clicked, button_id))

                # Stretch ratios: edit=4, delete=1  →  80% / 20%
                row_layout.addWidget(edit_btn, stretch=4)
                row_layout.addWidget(delete_btn, stretch=1)

                self.inner_layout.addWidget(row_widget)

            # Show "Add new button" only if the layer is not yet full
            if len(layer_buttons) < max_buttons:
                add_new_btn = RadialInterfaceSettingsButton(
                    "Add new button", parent=self.inner_widget
                )
                add_new_btn.clicked.connect(self.on_add_button_clicked)
                self.inner_layout.addWidget(add_new_btn)

    def on_add_button_clicked(self):
        """
        Handle the add button click event.
        Opens the RadialInterfaceButtonSettings window for a new button on this layer.
        """
        if DEBUG:
            DebugLogger.log("on_add_button_clicked called")
        if self.settings_window:
            self.settings_window.open_button_settings(layer=self.layer)
        else:
            if DEBUG:
                DebugLogger.log("on_add_button_clicked: settings_window is None!")

    def on_edit_button_clicked(self, button_id):
        """
        Handle an Edit button click event.
        Opens the RadialInterfaceButtonSettings window pre-loaded with the given button.

        Args:
            button_id: ID of the button to edit
        """
        if DEBUG:
            DebugLogger.log(f"on_edit_button_clicked called for button_id={button_id}")
        if self.settings_window:
            self.settings_window.open_button_settings(button_id=button_id, layer=self.layer)
        else:
            if DEBUG:
                DebugLogger.log("on_edit_button_clicked: settings_window is None!")

    def on_delete_button_clicked(self, button_id):
        """
        Handle a Delete button click event.
        Removes the button from pastewheel_config.json and refreshes the tab.

        Args:
            button_id: ID of the button to delete
        """
        if DEBUG:
            DebugLogger.log(f"on_delete_button_clicked called for button_id={button_id}")
        config = PasteWheelConfig()
        removed = config.remove_button(button_id)
        if DEBUG:
            DebugLogger.log(f"remove_button({button_id}) returned {removed}")
        self._refresh()

    def _refresh(self):
        """
        Clear all widgets from inner_layout and re-populate from the current config.
        Called after a button is deleted so the list updates without reopening the window.
        """
        # Remove all child widgets from the inner layout
        while self.inner_layout.count():
            item = self.inner_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Re-populate with the updated config
        self._populate()
    
    def set_enabled(self, enabled):
        """
        Set whether the tab is enabled (visible and clickable).
        
        Args:
            enabled: Boolean indicating tab visibility and interaction state
        """
        self.is_enabled = enabled
        self.setEnabled(enabled)
        
        if enabled:
            self.show()
        else:
            self.hide()
    
    def is_tab_enabled(self):
        """
        Get whether the tab is currently enabled.
        
        Returns:
            Boolean indicating if tab is enabled
        """
        return self.is_enabled
