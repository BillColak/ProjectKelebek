import os
import sys
from PyQt5.QtWidgets import *
from multiprocessing import freeze_support

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from kelebek_window import KelebekWindow

# TODO Possibly Implement Sherlock.
# TODO in app User Chat and Project Sharing.


if __name__ == '__main__':
    freeze_support()
    app = QApplication(sys.argv)

    # https://github.com/retejs/rete
    # https://github.com/kousun12/eternal
    # https://stackoverflow.com/questions/59966120/how-to-add-statichtml-css-js-etc-files-in-pyinstaller-to-create-standalone
    #

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = KelebekWindow()
    wnd.show()

    sys.exit(app.exec_())

