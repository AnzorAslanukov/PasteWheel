from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QScrollArea, QTableView, QAbstractItemView, QLineEdit)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt5.QtGui import QColor, QFont
import emoji as emoji_lib  # type: ignore

# Local imports (assuming they are in the correct path)
from theme import Theme
from radial_interface_button_settings.emoji_symbol_picker.esp_label import EspLabel
from radial_interface_button_settings.emoji_symbol_picker.esp_btn import EspBtn
from pastewheel_config import PasteWheelConfig


# Constants
EMOJI_CELL_WIDTH = 80       # Width of each emoji cell in pixels
EMOJI_CELL_HEIGHT = 48      # Height of each emoji cell in pixels
EMOJI_FONT_SIZE = 30        # Font size for emoji display in pixels
EMOJI_CELL_PADDING = 0      # Padding inside each emoji cell in pixels
EMOJI_TABLE_PADDING = 8     # Padding around the entire table in pixels
EMOJI_COLUMN_COUNT = 4      # Number of columns in the emoji grid

# Data Model Class
class EmojiTableModel(QAbstractTableModel):
    """
    Table model for displaying emoji data in a grid.
    Optimized to display emojis in a multi-column grid.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.emoji_list = []
        self._row_count = 0

    def set_emoji_data(self, emoji_data: dict):
        """Sets the emoji data for the model and updates the layout."""
        self.beginResetModel()
        self.emoji_list = sorted(emoji_data.items(), key=lambda item: item[0])
        self._row_count = (len(self.emoji_list) + EMOJI_COLUMN_COUNT - 1) // EMOJI_COLUMN_COUNT
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return self._row_count

    def columnCount(self, parent=QModelIndex()):
        return EMOJI_COLUMN_COUNT

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        emoji_index = (index.row() * EMOJI_COLUMN_COUNT) + index.column()
        if emoji_index >= len(self.emoji_list):
            return None

        code, info = self.emoji_list[emoji_index]

        if role == Qt.DisplayRole:
            return emoji_lib.emojize(code, language='alias')
        if role == Qt.ToolTipRole:
            return info.get("description", "")
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if role == Qt.FontRole:
            font = QFont()
            font.setPixelSize(EMOJI_FONT_SIZE)
            return font
            
        return None

# Main Widget Class
class EmojiSymbolPicker(QWidget):
    """
    A widget for picking emojis and symbols with theme support.
    """
    class _EmojiSymbolSelection(QWidget):
        """
        A scrollable widget for displaying categorized emoji results.
        Manages global selection state across all its internal table views.
        """
        CATEGORIES = {
            "smiley": "Smileys", "nature": "Nature", "food": "Food/Drink",
            "activities": "Activities", "travel": "Travel", "objects": "Objects",
            "symbols": "Symbols", "flags": "Flags"
        }

        def __init__(self, picker_instance, parent=None):
            super().__init__(parent)
            self.picker_instance = picker_instance  # Store reference to EmojiSymbolPicker
            self.theme = Theme()
            self.colors = self.theme.get_colors()
            
            self.all_table_views = []
            self.category_widgets = {} # Stores {'label': QLabel, 'model': QTableModel, 'table': QTableView}

            # --- Search-specific components ---
            self.search_model = EmojiTableModel()
            self.search_results_label = EspLabel("----- Search Results -----", display_alignment="center", bordered=False)
            self.search_table_view = self._create_table_view(self.search_model)
            
            # --- Container for categories ---
            self.categories_container = QWidget()
            self.categories_layout = QVBoxLayout(self.categories_container)
            self.categories_layout.setSpacing(10)
            self.categories_layout.setContentsMargins(0,0,0,0)

            self._fully_populated = False
            self._init_ui()  # Init UI first
            self._apply_styling()

        def showEvent(self, event):
            """Override showEvent to populate models only when window is shown."""
            super().showEvent(event)
            self._populate_models_if_needed()

        def _populate_models_if_needed(self):
            """Populates models with emoji data only if they haven't been already."""
            if self._fully_populated:
                return

            self._populate_models()
            self.show_categories() # Show all categories by default after populating.
            self._fully_populated = True

        def filter_by_search(self, search_text: str):
            """Filters the view to show only emojis matching the search text."""
            if not search_text:
                # If search is cleared, show the categories again
                self.show_categories()
                return

            all_emojis = PasteWheelConfig.get_all_emojis()
            
            # Filter based on description (case-insensitive)
            filtered_data = {
                code: info for code, info in all_emojis.items()
                if search_text.lower() in info.get("description", "").lower()
            }
            
            self.search_model.set_emoji_data(filtered_data)
            
            # Hide categories and show search results
            self.categories_container.hide()
            self.search_results_label.show()
            self.search_table_view.show()
            
            # Adjust height of search table
            new_height = self.search_model.rowCount() * EMOJI_CELL_HEIGHT + EMOJI_TABLE_PADDING
            self.search_table_view.setFixedHeight(new_height)

        def show_categories(self, category_id_to_show: str = None):
            """Shows all or a specific category, and hides the search results."""
            # Hide search results first
            self.search_results_label.hide()
            self.search_table_view.hide()
            
            # Show the category container
            self.categories_container.show()
            
            # Update visibility of individual categories within the container
            self.update_category_visibility(category_id_to_show)

        def update_category_visibility(self, visible_category_id: str = None):
            """Shows one or all categories within the categories container."""
            for cat_id, widgets in self.category_widgets.items():
                is_visible = (visible_category_id is None) or (cat_id == visible_category_id)
                widgets['label'].setVisible(is_visible)
                widgets['table'].setVisible(is_visible)

        def _init_ui(self):
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(10)

            # Add the category container to the layout
            content_layout.addWidget(self.categories_container)
            
            # This is now handled in _populate_models, which is called later.

            # Add search results components to the main layout, but hide them initially
            content_layout.addWidget(self.search_results_label)
            content_layout.addWidget(self.search_table_view)
            self.search_results_label.hide()
            self.search_table_view.hide()

            scroll_area.setWidget(content_widget)

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(scroll_area)

        def _populate_models(self):
            """Populates the models and creates the necessary widgets."""
            all_emojis = PasteWheelConfig.get_all_emojis()
            if not isinstance(all_emojis, dict):
                all_emojis = {}

            categorized_data = {cat_id: {} for cat_id in self.CATEGORIES}
            for code, info in all_emojis.items():
                category = (info.get("category") or "").strip().lower()
                if category in categorized_data:
                    categorized_data[category][code] = info

            for cat_id, cat_name in self.CATEGORIES.items():
                header_label = EspLabel(f"----- {cat_name} -----", display_alignment="center", bordered=False)
                model = EmojiTableModel()
                model.set_emoji_data(categorized_data.get(cat_id, {}))
                
                table_view = self._create_table_view(model)
                self.all_table_views.append(table_view)

                # Store all widgets for this category
                self.category_widgets[cat_id] = {'label': header_label, 'model': model, 'table': table_view}

                # Add them to the layout
                self.categories_layout.addWidget(header_label)
                self.categories_layout.addWidget(table_view)

                # Initially hide them
                header_label.hide()
                table_view.hide()

        def _create_table_view(self, model: EmojiTableModel) -> QTableView:
            table_view = QTableView()
            table_view.setModel(model)

            # --- Configuration ---
            table_view.setGridStyle(Qt.DotLine)
            table_view.setSelectionMode(QAbstractItemView.SingleSelection)
            table_view.setSelectionBehavior(QAbstractItemView.SelectItems)
            table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table_view.setAlternatingRowColors(False)
            table_view.verticalHeader().setVisible(False)
            table_view.horizontalHeader().setVisible(False)
            table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # --- Sizing ---
            table_view.verticalHeader().setDefaultSectionSize(EMOJI_CELL_HEIGHT)
            table_view.horizontalHeader().setDefaultSectionSize(EMOJI_CELL_WIDTH)
            total_width = EMOJI_COLUMN_COUNT * EMOJI_CELL_WIDTH + EMOJI_TABLE_PADDING
            total_height = model.rowCount() * EMOJI_CELL_HEIGHT + EMOJI_TABLE_PADDING
            table_view.setFixedSize(total_width, total_height)
            
            # --- Event Handling for Global Selection ---
            def custom_mouse_press_event(event):
                index = table_view.indexAt(event.pos())
                if index.isValid():
                    self._clear_all_selections()
                    table_view.selectionModel().select(index, table_view.selectionModel().Select)

                    # Emit signal with selected emoji
                    emoji_index = (index.row() * EMOJI_COLUMN_COUNT) + index.column()
                    if emoji_index < len(model.emoji_list):
                        code, info = model.emoji_list[emoji_index]
                        emoji_symbol = emoji_lib.emojize(code, language='alias')
                        # Emit the signal from the picker instance
                        self.picker_instance.emoji_selected.emit(emoji_symbol)

                    event.accept()
                else:
                    # Call original method if not handled
                    super(QTableView, table_view).mousePressEvent(event)
            table_view.mousePressEvent = custom_mouse_press_event

            # --- Styling ---
            table_style = f"""
                QTableView {{
                    background-color: {self.colors.get("table_background", "#FFFFFF")};
                    border: 1px solid {self.colors.get("table_border", "#E0E0E0")};
                    border-radius: 4px;
                    gridline-color: {self.colors.get("table_gridline", "#F0F0F0")};
                    color: {self.colors.get("table_text", "#000000")};
                    selection-background-color: {self.colors.get("table_selection_background", "#007BFF")};
                    selection-color: {self.colors.get("table_selection_text", "#FFFFFF")};
                }}
                QTableView::item {{ padding: {EMOJI_CELL_PADDING}px; }}
                QTableView::item:hover {{ background-color: {self.colors.get("table_hover_background", "#E8F4F8")}; }}
            """
            table_view.setStyleSheet(table_style)
            return table_view

        def _clear_all_selections(self):
            """Clear selections in all managed table views."""
            for table_view in self.all_table_views:
                table_view.selectionModel().clear()

        def _apply_styling(self):
            background_color = self.colors.get("section_background", "#F8F9FA")
            border_color = self.colors.get("border", "#CCCCCC")
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {background_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                }}
            """)

    # --- EmojiSymbolPicker Methods ---
    # Define signal for emoji selection
    emoji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.theme = Theme()
        self.colors = self.theme.get_colors()

        self._init_window(parent)
        self._init_ui()
        self._apply_styling()

    def _init_window(self, parent):
        """Initializes window properties like title, size, and position."""
        self.setWindowTitle("Emoji / Symbol Picker")
        self.setFixedSize(400, 600)

        if parent:
            self.move(parent.x() + 50, parent.y() + 50)
        else:
            self.move(100, 100)

    def _init_ui(self):
        """Initialize the main UI components and layout."""
        main_layout = QVBoxLayout(self)

        # 1. Search Section
        search_layout = self._create_search_section()
        main_layout.addLayout(search_layout)

        # 2. Categories Section
        categories_widget = self._create_categories_section()
        main_layout.addWidget(categories_widget)

        # 3. Emoji Selection Scroll Area
        self.emoji_selection_area = self._EmojiSymbolSelection(picker_instance=self)  
        main_layout.addWidget(self.emoji_selection_area)

    def _create_search_section(self):
        """Creates the top search bar layout."""
        search_layout = QHBoxLayout()
        self.search_prompt_label = EspLabel("Search:", margin=0, padding=0, bordered=False)
        
        # Use a standard QLineEdit for easier signal handling
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keyword...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        
        search_layout.addWidget(self.search_prompt_label)
        search_layout.addWidget(self.search_input)
        return search_layout

    def _create_categories_section(self):
        """Creates the grid of category selection buttons."""
        categories_container = QWidget()
        categories_container.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors.get("section_background", "#F0F0F0")};
                border-radius: 8px;
            }}
        """)
        
        layout = QGridLayout(categories_container)
        
        title_label = EspLabel("Select emoji or symbol category")
        layout.addWidget(title_label, 0, 0, 1, 4, Qt.AlignCenter)

        # --- Button Definitions ---
        self.category_buttons = {
            "smiley": EspBtn(text="Smiley"), "nature": EspBtn(text="Nature"),
            "food": EspBtn(text="Food/Drink"), "activities": EspBtn(text="Activities"),
            "travel": EspBtn(text="Travel"), "objects": EspBtn(text="Objects"),
            "symbols": EspBtn(text="Symbols"), "flags": EspBtn(text="Flags")
        }
        
        # --- Signal Connections ---
        for cat_id, button in self.category_buttons.items():
            # Pass both the button and its cat_id to the handler
            button.clicked.connect(lambda checked, b=button, cid=cat_id: self._on_category_button_clicked(b, cid))


        # --- Layout ---
        layout.addWidget(self.category_buttons["smiley"], 1, 0)
        layout.addWidget(self.category_buttons["nature"], 1, 1)
        layout.addWidget(self.category_buttons["food"], 1, 2)
        layout.addWidget(self.category_buttons["activities"], 1, 3)
        layout.addWidget(self.category_buttons["travel"], 2, 0)
        layout.addWidget(self.category_buttons["objects"], 2, 1)
        layout.addWidget(self.category_buttons["symbols"], 2, 2)
        layout.addWidget(self.category_buttons["flags"], 2, 3)

        return categories_container

    def _on_category_button_clicked(self, clicked_button: EspBtn, category_id: str):
        """Handles category button clicks for single selection and filtering."""
        
        # Clear search input when a category is clicked
        if self.search_input.text():
            self.search_input.clear()

        is_being_unchecked = not clicked_button.isChecked()

        for button in self.category_buttons.values():
            if button is not clicked_button:
                button.setChecked(False)
        
        if is_being_unchecked:
            self.emoji_selection_area.show_categories() # Show all
        else:
            self.emoji_selection_area.show_categories(category_id) # Show specific

    def _on_search_text_changed(self, text: str):
        """Handles search input changes to filter emojis."""
        # Uncheck all category buttons when a search is performed
        if text:
            for button in self.category_buttons.values():
                if button.isChecked():
                    button.setChecked(False)
        
        self.emoji_selection_area.filter_by_search(text)

    def clear_selection(self):
        """Clear the emoji selection in all table views."""
        if hasattr(self, 'emoji_selection_area'):
            self.emoji_selection_area._clear_all_selections()

    def _apply_styling(self):
        """Apply theme-based styling to the main window."""
        self.setStyleSheet(f"""
            EmojiSymbolPicker {{
                background-color: {self.colors.get("background", "#FFFFFF")};
                color: {self.colors.get("text", "#000000")};
                border: 1px solid {self.colors.get("border", "#CCCCCC")};
            }}
        """)
