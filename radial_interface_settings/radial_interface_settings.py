from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTabBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QToolTip
from radial_interface_settings.tabs.general_tab import GeneralTab
from radial_interface_settings.tabs.button_tab import ButtonTab
from theme import Theme
from pastewheel_config import PasteWheelConfig
from radial_interface_button_settings.radial_interface_button_settings import RadialInterfaceButtonSettings


class LockedTabBar(QTabBar):
    """
    Custom QTabBar that shows a ForbiddenCursor when the mouse hovers over
    a disabled (locked) tab, restores the default cursor otherwise, and
    displays the tab tooltip immediately (no delay) via QToolTip.showText().
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable mouse tracking so mouseMoveEvent fires without a button held down
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        index = self.tabAt(event.pos())
        if index != -1 and not self.isTabEnabled(index):
            self.setCursor(Qt.ForbiddenCursor)
            # Show tooltip immediately at the current global mouse position
            QToolTip.showText(event.globalPos(), self.tabToolTip(index))
        else:
            self.setCursor(Qt.ArrowCursor)
            QToolTip.hideText()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        QToolTip.hideText()
        super().leaveEvent(event)


class RadialInterfaceSettings(QWidget):
    # Emitted after any button is saved or deleted so that the radial
    # interface can re-render its button widgets with the latest config data.
    buttons_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = 400
        self.height = 400
        self.button_settings_windows = []  # List to keep references to windows
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        self.initUI()

    def initUI(self):
        """Initialize the RadialInterfaceSettings UI."""
        self.setWindowTitle('PasteWheel Settings')
        self.setGeometry(100, 100, self.width, self.height)
        
        # Apply theme colors to the window background and text
        background_color = self.colors.get("background", "#FFFFFF")
        foreground_color = self.colors.get("foreground", "#000000")
        button_color = self.colors.get("button", "#F0F0F0")
        button_hover_color = self.colors.get("button_hover", "#E0E0E0")
        text_color = self.colors.get("text", "#000000")
        
        # Apply stylesheet with theme colors
        # QTabBar::tab:disabled styles the darkened/locked appearance for Layer 2 and Layer 3
        # when their unlock conditions are not yet met.
        disabled_tab_color = self.colors.get("text_secondary", "#999999")
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QTabWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QTabBar::tab {{
                background-color: {button_color};
                color: {text_color};
                padding: 5px 15px;
                border: 1px solid {foreground_color};
            }}
            QTabBar::tab:selected {{
                background-color: {foreground_color};
                color: {background_color};
            }}
            QTabBar::tab:hover:!disabled {{
                background-color: {button_hover_color};
            }}
            QTabBar::tab:disabled {{
                background-color: {button_color};
                color: {disabled_tab_color};
                opacity: 0.5;
            }}
        """)

        # Create tab widget with custom tab bar for locked-tab cursor behaviour.
        # Stored as self.tab_widget so _on_button_saved can update tab states.
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(LockedTabBar())
        tab_widget = self.tab_widget  # local alias for readability below

        # Get config to determine layer unlock conditions:
        # Layer 2 unlocks when Layer 1 has at least one expand-type button.
        # Layer 3 unlocks when Layer 2 has at least one expand-type button.
        config = PasteWheelConfig()
        layer_2_unlocked = config.has_expand_button_in_layer(1)
        layer_3_unlocked = config.has_expand_button_in_layer(2)

        # Create and add tabs — all three layer tabs are always present
        general_tab = GeneralTab()
        tab_widget.addTab(general_tab, "General")

        # Layer 1 is always visible and enabled
        self.layer_1_buttons = ButtonTab(layer=1, enabled=True, settings_window=self)
        tab_widget.addTab(self.layer_1_buttons, "Layer 1")

        # Layer 2: always visible, enabled only if Layer 1 has an expand button.
        # Show an explanatory tooltip when locked.
        layer_2_tooltip = (
            "" if layer_2_unlocked
            else "Layer 1 requires at least one Expand button to unlock Layer 2."
        )
        self.layer_2_buttons = ButtonTab(
            layer=2,
            enabled=layer_2_unlocked,
            settings_window=self,
            tooltip=layer_2_tooltip
        )
        tab_widget.addTab(self.layer_2_buttons, "Layer 2")
        tab_widget.setTabEnabled(2, layer_2_unlocked)
        tab_widget.setTabToolTip(2, self.layer_2_buttons.tooltip)

        # Layer 3: always visible, enabled only if Layer 2 has an expand button.
        # Show an explanatory tooltip when locked.
        layer_3_tooltip = (
            "" if layer_3_unlocked
            else "Layer 2 requires at least one Expand button to unlock Layer 3."
        )
        self.layer_3_buttons = ButtonTab(
            layer=3,
            enabled=layer_3_unlocked,
            settings_window=self,
            tooltip=layer_3_tooltip
        )
        tab_widget.addTab(self.layer_3_buttons, "Layer 3")
        tab_widget.setTabEnabled(3, layer_3_unlocked)
        tab_widget.setTabToolTip(3, self.layer_3_buttons.tooltip)
        
        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def open_button_settings(self, button_id=None, layer=None, parent_id=None):
        """
        Open the RadialInterfaceButtonSettings window.

        Args:
            button_id: ID of the button to configure (optional, for editing existing buttons)
            layer: Layer number (1, 2, or 3) the button will belong to (optional)
            parent_id: ID of the parent expand button (for layer 2/3 child buttons, optional)
        """
        button_settings = RadialInterfaceButtonSettings(
            button_id=button_id, layer=layer, parent=self, parent_id=parent_id
        )
        self.button_settings_windows.append(button_settings)
        # Refresh the correct tab and re-evaluate layer lock states after save
        from functools import partial
        button_settings.button_saved.connect(partial(self._on_button_saved, layer))
        button_settings.show()

    def _on_button_saved(self, layer):
        """
        Called when a button is saved in RadialInterfaceButtonSettings.

        Refreshes the ButtonTab for the saved layer so the new button appears
        immediately, then delegates lock-state re-evaluation to
        _update_tab_lock_states().

        Args:
            layer: The layer number (1, 2, or 3) that was just written to.
        """
        tab_map = {
            1: self.layer_1_buttons,
            2: self.layer_2_buttons,
            3: self.layer_3_buttons,
        }
        tab = tab_map.get(layer)
        if tab is not None:
            tab._refresh()

        self._update_tab_lock_states()

    def _update_tab_lock_states(self):
        """
        Re-read the config and synchronise the Layer 2 / Layer 3 tab states.

        Called after every save and every deletion so that:
          - Adding a Layer-1 expand button unlocks the Layer-2 tab immediately.
          - Deleting the last Layer-1 expand button locks the Layer-2 tab.
          - The same logic applies between Layer 2 and Layer 3.
          - Layer 2 and Layer 3 tab content is always refreshed so stale
            messages (e.g. "No expand buttons found") are replaced with
            current data.
        """
        config = PasteWheelConfig()
        layer_2_unlocked = config.has_expand_button_in_layer(1)
        layer_3_unlocked = config.has_expand_button_in_layer(2)

        # Update the tab bar clickability
        self.tab_widget.setTabEnabled(2, layer_2_unlocked)
        self.tab_widget.setTabEnabled(3, layer_3_unlocked)

        # Keep the ButtonTab interaction state in sync
        self.layer_2_buttons.set_enabled(layer_2_unlocked)
        self.layer_3_buttons.set_enabled(layer_3_unlocked)

        # Always refresh Layer 2 and Layer 3 content so they reflect the
        # current config (handles both unlock and lock transitions).
        self.layer_2_buttons._refresh()
        self.layer_3_buttons._refresh()

        # Notify the radial interface (and any other listeners) that the
        # button set has changed so they can re-render their widgets.
        self.buttons_changed.emit()
