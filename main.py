import os
import sys
from PyQt5.QtWidgets import *

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".."))

from kelebek_window import KelebekWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = KelebekWindow()
    wnd.show()

    sys.exit(app.exec_())

# TODO Software Architecture will be: nodes connecting operations through generators and exec at the end.
