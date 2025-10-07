from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap, QFont, QPen
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
import math
import sys

class UIRenderer(QWidget):
    buttonClicked = pyqtSignal(str)  # Signal for button clicks

    def __init__(self):
        super().__init__()
        self.layer_radii = {1: 50, 2: 100, 3: 150}
        self.buttons = []  # List of buttons to draw
        self.center = QPointF(0, 0)
        self.button_images = {}  # Cache for QPixmap
        self.show_circles = False
        self.circles_positions = []

        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 300)
        self.hide()

    def show_window(self, center_x, center_y, show_circles=False):
        self.center = QPointF(center_x, center_y)
        self.move(int(center_x - 150), int(center_y - 150))
        if show_circles:
            self.show_circles = True
            self.circles_positions = []
            angles = [0, 90, 180, 270]
            radius = 50  # Distance from center
            for angle in angles:
                angle_rad = math.radians(angle)
                x = 150 + radius * math.cos(angle_rad)
                y = 150 + radius * math.sin(angle_rad)
                self.circles_positions.append((x, y))
        else:
            self.show_circles = False
            self.circles_positions.clear()
        self.update()
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_window(self):
        self.hide()
        self.buttons.clear()
        self.button_images.clear()

    def set_buttons(self, buttons):
        self.buttons = buttons
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw concentric circles
        painter.setPen(QPen(Qt.gray, 1))
        painter.setBrush(Qt.NoBrush)
        for radius in self.layer_radii.values():
            painter.drawEllipse(150 - radius, 150 - radius, 2 * radius, 2 * radius)

        # Draw buttons
        for button in self.buttons:
            self._draw_button(painter, button)

        # Draw circles if enabled
        if self.show_circles:
            for x, y in self.circles_positions:
                painter.setPen(QPen(Qt.white, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(int(x - 15), int(y - 15), 30, 30)

    def _draw_button(self, painter, button):
        if button.angle is None:
            return
        angle_rad = math.radians(button.angle)
        radius = self.layer_radii.get(button.layer, 50)
        x = 150 + radius * math.cos(angle_rad)
        y = 150 + radius * math.sin(angle_rad)
        button_size = 30
        rect = QRectF(x - button_size // 2, y - button_size // 2, button_size, button_size)

        if button.identifier_type == 'color':
            painter.setPen(QPen(Qt.white, 1))
            painter.setBrush(QColor(button.identifier_value))
            painter.drawEllipse(rect)
        elif button.identifier_type in ['string', 'emoji']:
            painter.setPen(QPen(Qt.white, 1))
            painter.setBrush(Qt.blue)
            painter.drawEllipse(rect)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(rect, Qt.AlignCenter, button.identifier_value)
        elif button.identifier_type == 'image':
            # Load and cache QPixmap
            if button.identifier_value not in self.button_images:
                pixmap = QPixmap(button.identifier_value)
                if pixmap.isNull():
                    pixmap = QPixmap(button_size, button_size)
                    pixmap.fill(Qt.red)  # Fallback
                else:
                    pixmap = pixmap.scaled(button_size, button_size, Qt.KeepAspectRatio)
                self.button_images[button.identifier_value] = pixmap
            pixmap = self.button_images[button.identifier_value]
            painter.drawPixmap(rect.toRect(), pixmap)

        # Label with button id for debugging
        painter.setFont(QFont("Arial", 8))
        painter.drawText(rect.bottomLeft().x(), rect.bottomLeft().y() + 15, button.id)

    def mousePressEvent(self, event):
        # Simple hit detection: check distance to center
        click_pos = event.pos()
        for button in self.buttons:
            if button.angle is None:
                continue
            angle_rad = math.radians(button.angle)
            radius = self.layer_radii.get(button.layer, 50)
            expected_x = 150 + radius * math.cos(angle_rad)
            expected_y = 150 + radius * math.sin(angle_rad)
            distance = math.hypot(click_pos.x() - expected_x, click_pos.y() - expected_y)
            if distance < 15:  # Within button radius
                self.buttonClicked.emit(button.id)
                return

    def resizeEvent(self, event):
        # Ensure window is 300x300
        super().resizeEvent(event)
        if self.size() != event.oldSize():
            self.resize(300, 300)

if __name__ == "__main__":
    # Example usage
    app = QApplication(sys.argv)
    # ui = UIRenderer()
    # ui.show()
    # sys.exit(app.exec_())
    pass
