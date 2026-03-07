from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel, QFrame
)
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

DELETE_ICON_PATH    = "assets/delete_icon.svg"
CLIPBOARD_ICON_PATH = "assets/clipboard_icon.svg"
EXPAND_ICON_PATH    = "assets/expand_icon.svg"

# Maximum number of buttons allowed per layer (per-parent for layers 2 and 3)
LAYER_MAX_BUTTONS = {1: 8, 2: 16, 3: 24}

# 8 accent colors for the 8 possible parent expand buttons — one palette per theme.
# Light mode: medium-dark, readable on white/light backgrounds.
# Dark mode: lighter/pastel, readable on dark backgrounds.
PARENT_COLORS_LIGHT = [
    "#1565C0",  # Blue
    "#2E7D32",  # Green
    "#E65100",  # Orange
    "#6A1B9A",  # Purple
    "#00695C",  # Teal
    "#C62828",  # Red
    "#4E342E",  # Brown
    "#283593",  # Indigo
]

PARENT_COLORS_DARK = [
    "#64B5F6",  # Light Blue
    "#81C784",  # Light Green
    "#FFB74D",  # Light Orange
    "#CE93D8",  # Light Purple
    "#4DB6AC",  # Light Teal
    "#EF9A9A",  # Light Red
    "#BCAAA4",  # Light Brown
    "#9FA8DA",  # Light Indigo
]


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
        self._theme_mode = Theme.get_mode()

        # Set color properties from theme
        self.color_background = colors.get("background", "#FFFFFF")
        self.color_foreground = colors.get("foreground", "#000000")
        self.color_button = colors.get("button", "#F0F0F0")
        self.color_button_hover = colors.get("button_hover", "#E0E0E0")
        self.color_text = colors.get("text", "#000000")
        self.color_text_secondary = colors.get("text_secondary", "#666666")
        self.color_border = colors.get("border", "#CCCCCC")
        self.color_accent = colors.get("accent", "#007BFF")

        # Choose the correct parent-color palette based on theme
        self._parent_colors = (
            PARENT_COLORS_DARK if self._theme_mode == "dark" else PARENT_COLORS_LIGHT
        )

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

    def _make_type_icon_label(self, button_type: str) -> "QLabel":
        """
        Build a QLabel containing the clipboard or expand SVG icon.

        The label is given no fixed size so it participates in the row's
        stretch layout (stretch=1, same as the delete button) and the icon
        is centred inside it.

        Args:
            button_type: ``"clip"`` for clipboard icon, ``"exp"`` for expand icon.

        Returns:
            QLabel with the rendered SVG pixmap, or an empty QLabel if the
            SVG file cannot be loaded.
        """
        icon_path = CLIPBOARD_ICON_PATH if button_type == "clip" else EXPAND_ICON_PATH
        label = QLabel(self.inner_widget)
        label.setAlignment(Qt.AlignCenter)

        renderer = QSvgRenderer(icon_path)
        if not renderer.isValid():
            return label

        size = QSize(24, 24)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()
        label.setPixmap(pixmap)
        return label

    def _make_button_row(self, btn_data, delete_icon):
        """
        Build a single [Type icon | Edit | Delete] row widget for a saved button.

        The type icon (clipboard or expand SVG) occupies the same proportional
        width as the delete button (stretch=1 each), while the edit button
        takes the remaining space (stretch=4).

        Args:
            btn_data: Button data dict from config.
            delete_icon: QIcon to use for the delete button.

        Returns:
            QWidget containing the row layout.
        """
        button_id = btn_data.get("id", "")
        label = btn_data.get("label", button_id)
        button_type = btn_data.get("button_type", "clip")

        row_widget = QWidget(self.inner_widget)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        # Type icon — same stretch weight as the delete button
        type_icon_label = self._make_type_icon_label(button_type)
        type_icon_label.setParent(row_widget)

        edit_btn = RadialInterfaceSettingsButton(f"Edit: {label}", parent=row_widget)
        edit_btn.clicked.connect(partial(self.on_edit_button_clicked, button_id))

        delete_btn = QPushButton(row_widget)
        delete_btn.setIcon(delete_icon)
        delete_btn.setIconSize(QSize(20, 20))
        delete_btn.setToolTip("Delete this button")
        delete_btn.setCursor(Qt.PointingHandCursor)
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

        row_layout.addWidget(type_icon_label, stretch=1)
        row_layout.addWidget(edit_btn, stretch=4)
        row_layout.addWidget(delete_btn, stretch=1)
        return row_widget

    def _populate(self):
        """
        Populate the tab with buttons based on the current configuration.

        Layer 1 behaviour (unchanged):
          - No buttons → show "Add first clipboard button" placeholder
          - 1 to (max-1) buttons → [Edit | Delete] rows + "Add new button"
          - Full → [Edit | Delete] rows only

        Layer 2 / Layer 3 behaviour (new):
          - For each expand button in the parent layer, render a color-coded
            section showing that parent's child buttons and an
            "Add button for: {label}" button (if < per-parent max).
          - If no expand buttons exist in the parent layer, show a message
            (this state should not occur since the tab is locked otherwise).
        """
        if self.layer == 1:
            self._populate_layer1()
        else:
            self._populate_child_layer()

    def _populate_layer1(self):
        """Populate the Layer 1 tab (original behaviour)."""
        config = PasteWheelConfig()
        layer_buttons = config.get_buttons_by_layer(1) or []
        max_buttons = LAYER_MAX_BUTTONS.get(1, 8)

        if not layer_buttons:
            add_button = RadialInterfaceSettingsButton(
                "Add first\nclipboard button", parent=self.inner_widget
            )
            add_button.clicked.connect(self.on_add_button_clicked)
            self.inner_layout.addWidget(add_button, alignment=Qt.AlignCenter)
        else:
            delete_icon = self._make_delete_icon()

            for btn_data in layer_buttons:
                row = self._make_button_row(btn_data, delete_icon)
                self.inner_layout.addWidget(row)

            if len(layer_buttons) < max_buttons:
                add_new_btn = RadialInterfaceSettingsButton(
                    "Add new button", parent=self.inner_widget
                )
                add_new_btn.clicked.connect(self.on_add_button_clicked)
                self.inner_layout.addWidget(add_new_btn)

    def _populate_child_layer(self):
        """
        Populate a Layer 2 or Layer 3 tab with color-coded sections,
        one section per expand button in the parent layer.
        """
        config = PasteWheelConfig()
        parent_layer = self.layer - 1
        expand_buttons = config.get_expand_buttons_by_layer(parent_layer)
        max_children = LAYER_MAX_BUTTONS.get(self.layer, 16)

        if not expand_buttons:
            # Shouldn't normally be visible, but handle gracefully
            msg = QLabel(
                f"No expand buttons found in Layer {parent_layer}.\n"
                "Add an Expand-type button there first."
            )
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet(f"color: {self.color_text_secondary};")
            self.inner_layout.addWidget(msg)
            return

        delete_icon = self._make_delete_icon()

        for idx, parent_btn in enumerate(expand_buttons):
            color = self._parent_colors[idx % len(self._parent_colors)]
            parent_id = parent_btn.get("id", "")
            parent_label = parent_btn.get("label", parent_id)

            # ── Section container ────────────────────────────────────────────
            section = QWidget(self.inner_widget)
            section_layout = QVBoxLayout(section)
            section_layout.setContentsMargins(8, 6, 8, 8)
            section_layout.setSpacing(4)

            # Left-border accent + subtle background tint
            section.setStyleSheet(f"""
                QWidget {{
                    border-left: 3px solid {color};
                    background-color: transparent;
                }}
            """)

            # ── Section header ───────────────────────────────────────────────
            header = QLabel(f"▶  {parent_label}  ({parent_id})")
            header.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 11pt;
                    border-left: none;
                    background-color: transparent;
                    padding: 2px 0px;
                }}
            """)
            section_layout.addWidget(header)

            # ── Separator line ───────────────────────────────────────────────
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet(f"color: {color}; border-color: {color};")
            section_layout.addWidget(line)

            # ── Existing child buttons ───────────────────────────────────────
            children = config.get_child_buttons_by_parent(parent_id)
            for child_data in children:
                row = self._make_button_row(child_data, delete_icon)
                section_layout.addWidget(row)

            # ── "Add button for: {label}" ────────────────────────────────────
            if len(children) < max_children:
                add_btn = RadialInterfaceSettingsButton(
                    f"Add button for: {parent_label}", parent=section
                )
                # Style the add button with the parent's accent color as border
                add_btn.setStyleSheet(add_btn.styleSheet() + f"""
                    QPushButton {{
                        border: 1px solid {color};
                    }}
                """)
                add_btn.clicked.connect(
                    partial(self.on_add_child_button_clicked, parent_id)
                )
                section_layout.addWidget(add_btn)

            self.inner_layout.addWidget(section)

    def on_add_button_clicked(self):
        """
        Handle the add button click event for Layer 1.
        Opens the RadialInterfaceButtonSettings window for a new button on this layer.
        """
        if DEBUG:
            DebugLogger.log("on_add_button_clicked called")
        if self.settings_window:
            self.settings_window.open_button_settings(layer=self.layer)
        else:
            if DEBUG:
                DebugLogger.log("on_add_button_clicked: settings_window is None!")

    def on_add_child_button_clicked(self, parent_id):
        """
        Handle the "Add button for: {label}" click for layers 2 and 3.
        Opens the RadialInterfaceButtonSettings window with the parent_id set.

        Args:
            parent_id: ID of the parent expand button this child belongs to.
        """
        if DEBUG:
            DebugLogger.log(f"on_add_child_button_clicked called for parent_id={parent_id}")
        if self.settings_window:
            self.settings_window.open_button_settings(layer=self.layer, parent_id=parent_id)
        else:
            if DEBUG:
                DebugLogger.log("on_add_child_button_clicked: settings_window is None!")

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
        while self.inner_layout.count():
            item = self.inner_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

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