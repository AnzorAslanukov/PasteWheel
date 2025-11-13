from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from theme import Theme
from radial_interface_button_settings.ribs_button import RibsButton
from radial_interface_button_settings.ribs_label import RibsLabel  # This was the missing import
from radial_interface_button_settings.ribs_checkbox import RibsCheckbox
from radial_interface_button_settings.ribs_radio_btn import RibsRadioBtn
from radial_interface_button_settings.ribs_clipboard_editor import RibsClipboardEditor
from radial_interface_button_settings.emoji_symbol_picker.emoji_symbol_picker import EmojiSymbolPicker


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

        # Create clipboard section at the top
        self.clipboard_section = QWidget(self)
        self.clipboard_section.setFixedHeight(140)  # Increased height to accommodate all new widgets
        section_bg = self.colors.get("section_background", "#F0F0F0")
        self.clipboard_section.setStyleSheet(f"""
            QWidget {{
                background-color: {section_bg};
                border-radius: 8px;
            }}
        """)

        # Create clipboard label inside the section
        self.clipboard_label = RibsLabel("Clipboard Features", "display", self.clipboard_section)
        self.clipboard_label.setAlignment(Qt.AlignCenter)  # Center the text

        # Create additional widgets for clipboard section
        self.add_seq_1_clipboard = RibsLabel("Add clipboard data:", "display", self.clipboard_section)
        self.edit_seq_1_clipboard = RibsButton("Edit Clipboard", self.clipboard_section)

        # Create checkbox row widgets
        self.seq_2_checkbox_label = RibsLabel("Enable sequential clipboard? ⓘ", "display", self.clipboard_section,
                                             display_tooltip="Store two things in clipboard. Paste them sequentially.")
        self.seq_2_checkbox = RibsCheckbox("", False, self.clipboard_section)  # Empty text, unchecked by default
        # Connect checkbox to control button clickability
        self.seq_2_checkbox.stateChanged.connect(self._on_seq_2_checkbox_changed)

        # Create sequential clipboard row widgets
        self.add_seq_2_clipboard = RibsLabel("Add sequential clipboard data:", "display", self.clipboard_section)
        self.edit_seq_2_clipboard = RibsButton("Edit clipboard", clickable=False)

        # Layout for the clipboard section
        section_layout = QVBoxLayout(self.clipboard_section)
        section_layout.addWidget(self.clipboard_label, alignment=Qt.AlignCenter)

        # Horizontal layout for the label and button (first row)
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.add_seq_1_clipboard)
        controls_layout.addStretch()  # Push button to the right
        controls_layout.addWidget(self.edit_seq_1_clipboard)
        section_layout.addLayout(controls_layout)

        # Horizontal layout for the checkbox label and checkbox (second row)
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.seq_2_checkbox_label)
        checkbox_layout.addStretch()  # Push checkbox to the right
        checkbox_layout.addWidget(self.seq_2_checkbox)
        section_layout.addLayout(checkbox_layout)

        # Horizontal layout for sequential clipboard widgets (third row)
        sequential_layout = QHBoxLayout()
        sequential_layout.addWidget(self.add_seq_2_clipboard)
        sequential_layout.addStretch()  # Push button to the right
        sequential_layout.addWidget(self.edit_seq_2_clipboard)
        section_layout.addLayout(sequential_layout)

        # Add clipboard section to main layout at the top
        layout.addWidget(self.clipboard_section)

        # Instantiate the clipboard editors
        self.seq_1_clipboard_editor = RibsClipboardEditor(parent=self)
        self.seq_2_clipboard_editor = RibsClipboardEditor(parent=self, window_title="Sequence 2 Clipboard Editor")

        # Connect button click signals to open clipboard editors
        self.edit_seq_1_clipboard.clicked.connect(self._on_edit_seq_1_clipboard_clicked)
        self.edit_seq_2_clipboard.clicked.connect(self._on_edit_seq_2_clipboard_clicked)

        # Create button label section underneath clipboard_section
        self.btn_label_section = QWidget(self)
        self.btn_label_section.setFixedHeight(160)  # Increased height for grid layout and new tooltip widgets
        section_bg = self.colors.get("section_background", "#F0F0F0")
        self.btn_label_section.setStyleSheet(f"""
            QWidget {{
                background-color: {section_bg};
                border-radius: 8px;
            }}
        """)

        # Create button label section title
        self.btn_label_section_title = RibsLabel("Button label options ⓘ", "display", self.btn_label_section,
                                                 display_tooltip="Choose text or emoji/symbol labels." \
                                                 "\nRadio buttons select one option.")
        self.btn_label_section_title.setAlignment(Qt.AlignCenter)

        # Create grid layout widgets
        # Row 1, Column 1: Display label for characters
        self.rib_btn_title_char_disp_label = RibsLabel("Characters (max 3)", "display", self.btn_label_section)

        # Row 1, Column 2: Radio button for characters (checked=True)
        self.rib_btn_title_char_radio_btn = RibsRadioBtn("", checked=True, parent=self.btn_label_section)

        # Row 1, Column 3: Input label for characters
        self.rib_btn_title_char_input_label = RibsLabel("", 
                                                        "input", 
                                                        self.btn_label_section,
                                                        input_clickable_tooltip="Enter a three-character label for the button.", 
                                                        max_length=3, 
                                                        input_alignment="center")

        # Row 2, Column 1: Display label for symbols
        self.rib_btn_title_symbol_disp_label = RibsLabel("Emojis/Symbols", "display", self.btn_label_section)

        # Row 2, Column 2: Radio button for symbols (checked=False)
        self.rib_btn_title_symbol_radio_btn = RibsRadioBtn("", checked=False, parent=self.btn_label_section)

        # Row 2, Column 3: Button for choosing symbol (clickable=False)
        self.rib_btn_title_symbol_btn = RibsButton("Choose Emoji/Symbol", clickable=False, parent=self.btn_label_section)

        # Layout for the button label section
        btn_label_section_layout = QVBoxLayout(self.btn_label_section)
        btn_label_section_layout.addWidget(self.btn_label_section_title, alignment=Qt.AlignCenter)

        # Grid layout for the 2x3 widgets
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        # Add widgets to grid (row, column)
        grid_layout.addWidget(self.rib_btn_title_char_disp_label, 0, 0)      # Row 1, Col 1
        grid_layout.addWidget(self.rib_btn_title_char_radio_btn, 0, 1)       # Row 1, Col 2
        grid_layout.addWidget(self.rib_btn_title_char_input_label, 0, 2)     # Row 1, Col 3

        grid_layout.addWidget(self.rib_btn_title_symbol_disp_label, 1, 0)    # Row 2, Col 1
        grid_layout.addWidget(self.rib_btn_title_symbol_radio_btn, 1, 1)     # Row 2, Col 2
        grid_layout.addWidget(self.rib_btn_title_symbol_btn, 1, 2)           # Row 2, Col 3

        btn_label_section_layout.addLayout(grid_layout)

        # Add tooltip configuration row
        tooltip_row_layout = QHBoxLayout()
        self.rib_tooltip_disp_label = RibsLabel("Include tooltip? ⓘ", "display", self.btn_label_section,
                                                display_tooltip="Add an explanation that will show up when you hover your mouse over the button." \
                                                "\nYou can include a max of 128 characters.")
        self.rib_tooltip_checkbox = RibsCheckbox("", False, parent=self.btn_label_section)
        self.rib_tooltip_config_btn = RibsButton("Configure tooltip", clickable=False, parent=self.btn_label_section)

        tooltip_row_layout.addWidget(self.rib_tooltip_disp_label)  # Left
        tooltip_row_layout.addStretch()  # Space between label and checkbox
        tooltip_row_layout.addWidget(self.rib_tooltip_checkbox)   # Center
        tooltip_row_layout.addStretch()  # Space between checkbox and button
        tooltip_row_layout.addWidget(self.rib_tooltip_config_btn) # Right
        btn_label_section_layout.addLayout(tooltip_row_layout)

        # Connect tooltip checkbox to control config button clickability
        self.rib_tooltip_checkbox.stateChanged.connect(self._on_tooltip_checkbox_changed)

        # Connect radio buttons to control widget states
        self.rib_btn_title_char_radio_btn.toggled.connect(self._on_char_radio_toggled)
        self.rib_btn_title_symbol_radio_btn.toggled.connect(self._on_symbol_radio_toggled)

        # Connect button type radio buttons for mutual exclusivity
        # Note: setChecked(True) and signal connections must happen AFTER widget instantiation

        # Add button label section to main layout
        layout.addWidget(self.btn_label_section)

        # Create button type display label underneath btn_label_section
        self.rib_btn_type_disp_label = RibsLabel("Select button type ⓘ", "display", self,
                                                 padding=0,
                                                 display_tooltip="Clipboard button stores data." \
                                                 "\nExpand button reveals more buttons.")
        
        layout.addWidget(self.rib_btn_type_disp_label, alignment=Qt.AlignCenter)

        # Create button type selection widgets in a 2x2 grid
        # Row 1, Column 1: Display label for clipboard
        self.rib_radio_select_clipboard_disp_label = RibsLabel("Clipboard", "display", self, padding=0, size=[80, 15])

        # Row 1, Column 2: Display label for expand
        self.rib_radio_select_expand_disp_label = RibsLabel("Expand", "display", self, padding=0, size=[80, 15])

        # Row 2, Column 1: Radio button for clipboard (checked=True)
        self.rib_radio_select_clipboard = RibsRadioBtn("", checked=True, parent=self)

        # Row 2, Column 2: Radio button for expand (checked=False)
        self.rib_radio_select_expand = RibsRadioBtn("", checked=False, parent=self)

        # Create container widget for first row (clipboard label + radio) to enable centering
        type_row1_container = QWidget(self)
        type_row1_layout = QHBoxLayout(type_row1_container)
        type_row1_layout.addWidget(self.rib_radio_select_clipboard_disp_label)
        type_row1_layout.addWidget(self.rib_radio_select_clipboard)
        layout.addWidget(type_row1_container, alignment=Qt.AlignCenter)

        # Create container widget for second row (expand label + radio) to enable centering
        type_row2_container = QWidget(self)
        type_row2_layout = QHBoxLayout(type_row2_container)
        type_row2_layout.addWidget(self.rib_radio_select_expand_disp_label)
        type_row2_layout.addWidget(self.rib_radio_select_expand)
        layout.addWidget(type_row2_container, alignment=Qt.AlignCenter)

        # Set custom vertical spacing between the type selection rows - adjustable value
        layout.setSpacing(8)  # CUSTOM VALUE: Adjust this number to control vertical gap between rows

        # Create save button at the bottom
        self.save_button = RibsButton("Save button data", self)
        # To center the button, we can add stretch above it and center it
        layout.addStretch()  # This will push the button to the bottom
        layout.addWidget(self.save_button, alignment=Qt.AlignCenter)  # Center the button

        # Connect button type radio buttons for mutual exclusivity (AFTER widget instantiation)
        self.rib_radio_select_clipboard.setChecked(True)  # Ensure clipboard is initially checked
        self.rib_radio_select_clipboard.toggled.connect(self._on_clipboard_radio_toggled)
        self.rib_radio_select_expand.toggled.connect(self._on_expand_radio_toggled)

        # Defer instantiation of the emoji picker until it's needed
        self.emoji_symbol_picker = None

        # Connect symbol button to open emoji picker
        self.rib_btn_title_symbol_btn.clicked.connect(self._on_symbol_btn_clicked)

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

    def _on_seq_2_checkbox_changed(self, state):
        """
        Handle seq_2_checkbox state changes to control edit_seq_2_clipboard clickability.
        """
        # state ==  2 means checked (Qt.CheckState.Checked), state == 0 means unchecked
        is_checked = state == 2  # 2 is Qt.CheckState.Checked value
        self.edit_seq_2_clipboard.set_clickable(is_checked)

    def _on_char_radio_toggled(self, checked):
        """
        Handle rib_btn_title_char_radio_btn toggles to control widget states.

        When characters radio button is checked:
        - rib_btn_title_char_input_label remains clickable (True by default)
        - rib_btn_title_symbol_btn becomes non-clickable (False)
        - rib_btn_title_input_label becomes clickable (True)
        """
        if checked:
            # Characters radio is checked - character input should be enabled
            # Symbol button should be disabled
            self.rib_btn_title_symbol_btn.set_clickable(False)
            self.rib_btn_title_char_input_label.set_clickable(True)

    def _on_symbol_radio_toggled(self, checked):
        """
        Handle rib_btn_title_symbol_radio_btn toggles to control widget states.

        When symbols radio button is checked:
        - rib_btn_title_char_input_label becomes non-clickable (False)
        - rib_btn_title_char_radio_btn becomes unchecked (False)
        - rib_btn_title_symbol_btn becomes clickable (True)
        """
        if checked:
            # Symbols radio is checked - make character input non-clickable
            # and uncheck the character radio button (but this will trigger _on_char_radio_toggled)
            self.rib_btn_title_char_input_label.set_clickable(False)
            self.rib_btn_title_symbol_btn.set_clickable(True)

    def _on_tooltip_checkbox_changed(self, state):
        """
        Handle rib_tooltip_checkbox state changes to control rib_tooltip_config_btn clickability.
        """
        # state ==  2 means checked (Qt.CheckState.Checked), state == 0 means unchecked
        is_checked = state == 2  # 2 is Qt.CheckState.Checked value
        self.rib_tooltip_config_btn.set_clickable(is_checked)

    def _on_clipboard_radio_toggled(self, checked):
        """
        Handle rib_radio_select_clipboard toggles to ensure mutual exclusivity with expand radio.
        """
        if checked:
            # Clipboard radio was just checked - ensure expand is unchecked
            self.rib_radio_select_expand.setChecked(False)

    def _on_expand_radio_toggled(self, checked):
        """
        Handle rib_radio_select_expand toggles to ensure mutual exclusivity with clipboard radio.
        """
        if checked:
            # Expand radio was just checked - ensure clipboard is unchecked
            self.rib_radio_select_clipboard.setChecked(False)

    def _on_edit_seq_1_clipboard_clicked(self):
        """
        Handle edit_seq_1_clipboard button click to open seq_1_clipboard_editor.
        """
        self.seq_1_clipboard_editor.show()
        self.seq_1_clipboard_editor.raise_()
        self.seq_1_clipboard_editor.activateWindow()

    def _on_edit_seq_2_clipboard_clicked(self):
        """
        Handle edit_seq_2_clipboard button click to open seq_2_clipboard_editor.
        """
        self.seq_2_clipboard_editor.show()
        self.seq_2_clipboard_editor.raise_()
        self.seq_2_clipboard_editor.activateWindow()

    def _on_symbol_btn_clicked(self):
        """
        Handle rib_btn_title_symbol_btn click to open emoji_symbol_picker.
        Instantiates the picker on first click (lazy instantiation).
        """
        # Lazy instantiation: create the picker only when it's first needed
        if self.emoji_symbol_picker is None:
            self.emoji_symbol_picker = EmojiSymbolPicker(parent=self)
        
        self.emoji_symbol_picker.show()
        self.emoji_symbol_picker.raise_()
        self.emoji_symbol_picker.activateWindow()
