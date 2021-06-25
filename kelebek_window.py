import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from kelebek_browser import QtBrowserWidget, QuteBrowser

from nodeeditor.utils import loadStylesheets
from nodeeditor.node_editor_window import NodeEditorWindow
from kelebek_sub_window import KelebekSubWindow
# from kelebek_drag_listbox import QDMDragListbox
from kelebek_treeview import KelebekTreeView
from kelebek_node_factory import FactoryView
from kelebek_conf import *

from nodeeditor.utils import dumpException, pp

# Enabling edge validators
from nodeeditor.node_edge import Edge
from nodeeditor.node_edge_validators import *
# Edge.registerEdgeValidator(edge_validator_debug)
Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)

# images for the dark skin
import qss.nodeeditor_dark_resources

DEBUG = False
# TODO increase the zoom in factor
# TODO People should be able to make their own nodes and dashboard components. Ex: in-house vs custom. connect to
#  external .py files
# TODO Chat
# TODO Integrated Dashboard, maybe can integrate qt with local host server to utilise JS/Django shit.
# TODO https://stackoverflow.com/questions/3770084/efficiently-updating-a-qtableview-at-high-speed?rq=1
# https://dribbble.com/shots/15266170-Bitoket-cryptocurrency-UI-and-UX-Design-Darkmode/attachments/7017779?mode=media
# https://dribbble.com/shots/7797656-Tree-View/attachments/458993?mode=media
# https://dribbble.com/shots/13964955-Bitoket-cryptocurrency-Dashboard-UI-and-UX-Design
# https://dribbble.com/shots/14073238-Bitoket-cryptocurrency-Landing-page-design
# https://dribbble.com/shots/15423799-Admin-Dashboard
# https://dribbble.com/shots/15186334-Celsius-Web-App-Dashboard
# https://dribbble.com/shots/14645371-Socialy-Social-Media-Analytics-Dashboard
# https://dribbble.com/shots/15326758-Dashboard-for-My-Crowd-musician
# https://dribbble.com/shots/15325310-FinTech-Dashboard-Layout-samples *****
# https://stock.adobe.com/ca/283006387?as_channel=adobe_com&as_campclass=brand&as_campaign=srp-raill&as_source=behance_net&as_camptype=acquisition&as_audience=users&as_content=thumbnail-click&promoid=J7XBWPPS&mv=other&asset_id=361039498


class KelebekWindow(NodeEditorWindow):

    def initUI(self):
        self.name_company = 'GucciGang'
        self.name_product = 'Kelebek NodeEditor'

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        loadStylesheets(
            os.path.join(os.path.dirname(__file__), "qss/treeview.qss"),
            os.path.join(os.path.dirname(__file__), "qss/nodeeditor-dark.qss"),
            self.stylesheet_filename
        )

        self.empty_icon = QIcon(".")
        # app_icon = QIcon(os.path.join(os.path.dirname(__file__), "icons/purple-cube.ico"))
        app_icon = QIcon(os.path.join(os.path.dirname(__file__), "images/green-cube.svg"))
        self.setWindowIcon(app_icon)

        if DEBUG:
            print("Registered nodes:")
            pp(KELEBEK_NODES)
        # self.setWindowFlags(Qt.FramelessWindowHint) # Todo custom window frame to complete overall style

        self.initMDIArea()
        self.stackedWidget()
        self.toolBar()

        self.createActions()
        self.createMenus()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Kelebek NodeEditor")
        self.palette().setBrush(QPalette.Highlight, QBrush(Qt.transparent))

    def initMDIArea(self):

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        # self.nodesListWidget = QDMDragListbox()
        self.nodesTreeView = KelebekTreeView()
        self.nodesTreeView.doubleClicked.connect(self.tag_double_clicked)

        self.ui_search = QLineEdit()
        self.ui_search.setPlaceholderText('Search...')
        self.ui_search.textChanged.connect(self.search_text_changed)
        self.ui_search.setFont(QFont('Seqoe UI Symbol'))

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.palette().setBrush(QPalette.Highlight, QBrush(Qt.transparent))

        treeArea = QWidget()
        docklayout = QVBoxLayout()
        treeArea.setLayout(docklayout)
        docklayout.addWidget(self.ui_search)
        docklayout.addWidget(self.nodesTreeView)
        self.nodesDock.setWidget(treeArea)

        self.nodesDock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    def search_text_changed(self, text=None):
        self.nodesTreeView.tags_model.setFilterRegExp(self.ui_search.text())

        if len(self.ui_search.text()) >= 1 and self.nodesTreeView.tags_model.rowCount() > 0:
            self.nodesTreeView.expandAll()
        else:
            self.nodesTreeView.expandAll()

    def tag_double_clicked(self, idx):
        text = []
        while idx.isValid():
            text.append(idx.data(Qt.DisplayRole))
            idx = idx.parent()
        text.reverse()
        self.nodesTreeView.clickedTag.emit(text)

    def stackedWidget(self):
        central_widget = QWidget()
        self.stackedlay = QStackedLayout(central_widget)

        self.browser = QuteBrowser()
        self.kelebek_browser = QtBrowserWidget(self.browser)

        self.stackedlay.addWidget(self.kelebek_browser)
        self.stackedlay.addWidget(self.mdiArea)
        factory = FactoryView(self)
        self.stackedlay.addWidget(factory)

        self.setCentralWidget(central_widget)

    def toolBar(self):
        self.navtb = QToolBar("Toolbar")
        self.navtb.setIconSize(QSize(27, 27))
        self.addToolBar(Qt.LeftToolBarArea, self.navtb)

        self.file = QAction(QIcon('images/globe.svg'), "Browser", self)
        self.navtb.addAction(self.file)
        self.file.triggered.connect(self.window1)
        self.navtb.addSeparator()

        # self.dev_tools = QAction(QIcon('images/DevTools.png'), 'DevTools', self)
        # self.navtb.addAction(self.dev_tools)
        # self.dev_tools.triggered.connect(self.inspectorDialog)
        # self.navtb.addSeparator()

        self.filetree = QAction(QIcon('images/diagram-3-fill.svg'), "Node Editor", self)
        self.navtb.addAction(self.filetree)
        self.filetree.triggered.connect(self.window2)
        self.navtb.addSeparator()

        self.highlight = QAction(QIcon('images/blackhighlighter.svg'), 'Highlight', self)
        self.navtb.addAction(self.highlight)
        self.highlight.triggered.connect(self.kelebek_browser.inspect_element)
        self.navtb.addSeparator()

        self.play_btn = QAction(QIcon('images/chart.svg'), 'Chart', self)
        self.navtb.addAction(self.play_btn)
        # self.play_btn.triggered.connect(self.print_editor_widget)
        self.navtb.addSeparator()

        self.chat_btn = QAction(QIcon('images/chat.svg'), 'Chat', self)
        self.navtb.addAction(self.chat_btn)
        # self.chat_btn.triggered.connect(self.print_editor_widget)
        self.navtb.addSeparator()

        self.factory_btn = QAction(QIcon('icons/Factory.svg'), 'Factory', self)
        self.navtb.addAction(self.factory_btn)
        self.factory_btn.triggered.connect(self.window3)
        self.navtb.addSeparator()

    # def print_editor_widget(self):
        # KEEP THESE AS A REFERENCE
        # this was used to test adding nodes from webbrowser by the context manager.
        # active = self.getCurrentNodeEditorWidget()
        # print('Active:', active)
        # print('mdiArea:', self.mdiArea.subWindowList())
        # print('current window:', self.mdiArea.currentSubWindow().widget().scene)
        # print('window:', self.mdiArea.window())
        # print('Getting node from op code without scene: ', get_class_from_opcode(3))
        # print(self.mdiArea.ActivationHistoryOrder)

        # new_kelebek_node = get_class_from_opcode(3)
        # new_kelebek_node.setPos(0, 0)
    #     self.mdiArea.currentSubWindow()
    #     self.mdiArea.ActivationHistoryOrder
    #     self.mdiArea.
    # #     self.mdiArea.subWindowActivated.connect(self.whaever)
    #
    # def whaever(self, s):
    #     print(s)


    def window1(self):
        self.stackedlay.setCurrentIndex(0)

    def window2(self):
        self.stackedlay.setCurrentIndex(1)

    def window3(self):
        self.stackedlay.setCurrentIndex(2)

    # def inspectorDialog(self):
    #     self.inspector_dialog = InspectorDialog(self.browser)
    #     self.inspector_dialog.show()

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            # hacky fix for PyQt 5.14.x
            import sys
            sys.exit(0)

    def createActions(self):
        super().createActions()

        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def getCurrentNodeEditorWidget(self):
        """ we're returning NodeEditorWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e: dumpException(e)

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', self.getFileDialogDirectory(), self.getFileDialogFilter())

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we need to create new subWindow and open the file
                        nodeeditor = KelebekSubWindow()
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" % fname, 5000)
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e: dumpException(e)

    def about(self):
        QMessageBox.about(self, "About Kelebek NodeEditor",
                "The <b>Kelebek NodeEditor</b> example demonstrates how to write multiple "
                "document interface applications using PyQt5 and NodeEditor. For more information visit: "
                "<a href='https://www.blenderfreak.com/'>www.BlenderFreak.com</a>")

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)

        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def updateMenus(self):
        # print("update Menus")
        active = self.getCurrentNodeEditorWidget()
        # # print("active window menu:", active)

        if active is not None:
            self.browser.scene = active.scene
            # print('browser scene:', self.browser.scene)

        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)

        self.updateEditMenu()

    def updateEditMenu(self):
        try:
            # print("update Edit Menu")
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)

            self.actPaste.setEnabled(hasMdiChild)

            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e: dumpException(e)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())
        self.windowMenu.addSeparator()

        toolbar = self.windowMenu.addAction('Toolbar')
        toolbar.setCheckable(True)
        toolbar.triggered.connect(self.onWindowToolbar)
        toolbar.setCheckable(self.navtb.isVisible())
        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def onWindowToolbar(self):
        if self.navtb.isVisible():
            self.navtb.hide()
        else:
            self.navtb.show()

    # def createNodesDock(self):
    #     self.nodesListWidget = QDMDragListbox()
    #
    #     self.nodesDock = QDockWidget("Nodes")
    #     self.nodesDock.setWidget(self.nodesListWidget)
    #     self.nodesDock.setFloating(False)
    #
    #     self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
        # self.statusBar().addPermanentWidget(self.progressBar)

    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else KelebekSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)