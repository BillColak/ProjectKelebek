from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from kelebek_conf import *
from nodeeditor.utils import dumpException

Loco = {'Canada': {
    'West': {
        'British Columbia': {'Victoria', 'Vancouver'},
        'Alberta': {'Edmonton', 'Calgary'}
    }
},
    'America': {
        'California': {'San Francisco', 'San Jose', 'Oakland'},
        'Texas': {'Austin', 'Houston', 'Dallas'}
    },
    'Mexico': {}
}


class SearchProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(SearchProxyModel, self).__init__(parent)
        self.text = ''

    def setFilterRegExp(self, pattern):
        if isinstance(pattern, str):
            pattern = QRegExp(pattern, Qt.CaseInsensitive, QRegExp.FixedString)
        super(SearchProxyModel, self).setFilterRegExp(pattern)

    # Recursive search
    def _accept_index(self, idx):
        if idx.isValid():
            text = idx.data(Qt.DisplayRole)
            if self.filterRegExp().indexIn(text) >= 0:
                return True
            for row in range(idx.model().rowCount(idx)):
                if self._accept_index(idx.model().index(row, 0, idx)):
                    return True
        return False

    def filterAcceptsRow(self, sourceRow, sourceParent):
        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        return self._accept_index(idx)

    def lessThan(self, left, right):
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)
        return leftData < rightData


class KelebekTreeView(QTreeView):

    customMimeType = "application/x-customqstandarditemmodeldatalist"
    clickedTag = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tags_model = SearchProxyModel()
        self.tags_model.setSourceModel(QStandardItemModel())
        self.tags_model.setDynamicSortFilter(True)

        self.setModel(self.tags_model)
        model = self.tags_model.sourceModel()
        self.rootNode = model.invisibleRootItem()

        self.initUI()
        self.expandAll()

    def initUI(self):
        # init
        self.setIconSize(QSize(24, 24))
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setDragEnabled(True)
        self.setHeaderHidden(True)
        self.palette().setBrush(QPalette.Highlight, QBrush(Qt.transparent))
        self.addItems(self.rootNode, KELEBEK_NODES2)

    def drawRow(self, painter: QPainter, options: QStyleOptionViewItem, index: QModelIndex) -> None:
        options.palette.setColor(QPalette.Highlight, Qt.transparent)  # Hide the ugly blue selection rectangle.
        super().drawRow(painter, options, index)

    def addItems(self, parent, values):
        if isinstance(values, dict):
            for key, value in values.items():
                if isinstance(key, int):
                    node = value
                    self.addMyItem(parent, node.op_title, node.icon, node.op_code)
                else:
                    item = QStandardItem(key)
                    item.setToolTip('This is a treeview item tooltip1')
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    parent.appendRow(item)
                    self.addItems(item, value)

    def addMyItem(self, parent, name, icon=None, op_code=0):
        item = QStandardItem(name)
        item.setToolTip('This is a treeview item tooltip2')
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(pixmap, Qt.UserRole)
        item.setData(op_code, Qt.UserRole + 1)
        parent.appendRow(item)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.selectedIndexes()[0]
            op_code = item.data(Qt.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.data(0))

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(int(pixmap.width() / 2), int(pixmap.height() / 2)))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)
