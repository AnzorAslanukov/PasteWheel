import sys
from PyQt5.QtWidgets import QApplication
from radial_interface import RadialInterface


if __name__ == '__main__':
    app = QApplication(sys.argv)
    radial_interface = RadialInterface(width=400, height=400)
    radial_interface.show()
    sys.exit(app.exec_())
