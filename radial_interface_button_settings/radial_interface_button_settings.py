from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from theme import Theme
from radial_interface_button_settings.ribs_button import RibsButton
from radial_interface_button_settings.ribs_label import RibsLabel
from radial_interface_button_settings.ribs_checkbox import RibsCheckbox


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
        self.clipboard_section.setFixedHeight(110)  # Increased height to accommodate all new widgets
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

        # Add clipboard section to main layout at the top
        layout.addWidget(self.clipboard_section)

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
