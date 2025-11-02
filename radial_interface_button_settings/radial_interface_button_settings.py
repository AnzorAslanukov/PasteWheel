from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from theme import Theme
from radial_interface_button_settings.ribs_button import RibsButton
from radial_interface_button_settings.ribs_label import RibsLabel
from radial_interface_button_settings.ribs_checkbox import RibsCheckbox
from radial_interface_button_settings.ribs_radio_btn import RibsRadioBtn


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
        self.add_seq_1_clipboard = RibsLabel("Add clipboard data", "display", self.clipboard_section)
        self.edit_seq_1_clipboard = RibsButton("Edit Clipboard", self.clipboard_section)

        # Create checkbox row widgets
        self.seq_2_checkbox_label = RibsLabel("Enable sequential clipboard?", "display", self.clipboard_section)
        self.seq_2_checkbox = RibsCheckbox("", False, self.clipboard_section)  # Empty text, unchecked by default
        # Connect checkbox to control button clickability
        self.seq_2_checkbox.stateChanged.connect(self._on_seq_2_checkbox_changed)

        # Create sequential clipboard row widgets
        self.add_seq_2_clipboard = RibsLabel("Add sequential clipboard data", "display", self.clipboard_section)
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

        # Create button label section underneath clipboard_section
        self.btn_label_section = QWidget(self)
        self.btn_label_section.setFixedHeight(120)  # Increased height for grid layout
        section_bg = self.colors.get("section_background", "#F0F0F0")
        self.btn_label_section.setStyleSheet(f"""
            QWidget {{
                background-color: {section_bg};
                border-radius: 8px;
            }}
        """)

        # Create button label section title
        self.btn_label_section_title = RibsLabel("Button label options", "display", self.btn_label_section)
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

        # Add button label section to main layout
        layout.addWidget(self.btn_label_section)

        # Create button type display label underneath btn_label_section
        self.rib_btn_type_disp_label = RibsLabel("Select button type", "display", self, padding=0)
        layout.addWidget(self.rib_btn_type_disp_label, alignment=Qt.AlignCenter)

        # Create button type selection widgets in a 2x2 grid
        # Row 1, Column 1: Display label for clipboard
        self.rib_radio_select_clipboard_disp_label = RibsLabel("Clipboard", "display", self, padding=0)

        # Row 1, Column 2: Display label for expand
        self.rib_radio_select_expand_disp_label = RibsLabel("Expand", "display", self, padding=0)

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
