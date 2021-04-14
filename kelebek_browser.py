from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from jinja2 import Template
# import os

from kelebek_conf import *

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# HOME = 'https://www.google.com/'
HOME = "https://books.toscrape.com/"


# TODO custom menu does not pop up when user interacts with browser before editor widget. Need to update browser,
#  on the existence of a scene, also this might mean the browsers also has no communication if a scene is closed
#  leading to an error.


class Element(QtCore.QObject):
    def __init__(self, name, parent=None):
        super(Element, self).__init__(parent)
        self._name = name  # = 'xpath_helper'

    @property
    def name(self):
        return self._name

    def script(self):
        return ""


class WebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super(WebEnginePage, self).__init__(parent)
        self.loadFinished.connect(self.onLoadFinished)
        self._objects = []  # Helper object
        self._scripts = []  # only usage? more than one script?

    def add_object(self, obj):
        self._objects.append(obj)

    @QtCore.pyqtSlot(bool)
    def onLoadFinished(self, ok):
        print("Finished loading: ", ok)
        if ok:
            self.load_qwebchannel()
            self.add_objects()
            return ok

    def load_qwebchannel(self):
        file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.runJavaScript(content.data().decode())
        if self.webChannel() is None:
            channel = QWebChannel(self)
            self.setWebChannel(channel)

    def add_objects(self):
        if self.webChannel() is not None:
            objects = {obj.name: obj for obj in self._objects}  # 'xpath_helper': Helper object
            self.webChannel().registerObjects(objects)
            _script = """
            {% for obj in objects %}
            var {{obj}};
            {% endfor %}
            new QWebChannel(qt.webChannelTransport, function (channel) {
            {% for obj in objects %}
                {{obj}} = channel.objects.{{obj}};
            {% endfor %}
            }); 
            """
            self.runJavaScript(Template(_script).render(objects=objects.keys()))
            for obj in self._objects:
                if isinstance(obj, Element):
                    self.runJavaScript(obj.script())


class Helper(Element):  # this is the object
    xpathClicked = QtCore.pyqtSignal(str, str, str, str, str, str, str, str, str)

    def script(self):
        js = ""
        file = QtCore.QFile(os.path.join(CURRENT_DIR, "xpath_from_element.js"))
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            js = content.data().decode()

        js += """
            function getElementAttrs(el) {
              return [].slice.call(el.attributes).map((attr) => {
                return {
                  name: attr.name,
                  value: attr.value
                }
              });
            }
            document.addEventListener('contextmenu', function(e) {
                e = e || window.event;
                var target = e.target || e.srcElement;
                var xpath = Elements.DOMPath.xPath(target, false);
                var local_name = target.localName;
                var parent_name = target.parentNode.localName;
                var text = target.innerText;
                var class_name = target.className;
                var image = target.getAttribute("src");
                var link = target.href;
                var allAttrs = getElementAttrs(target);
                var onlyAttrNames = allAttrs.map(attr => attr.name).toString();
                var onlyAttrValues = allAttrs.map(attr => attr.value).toString();
                {{name}}.receive_xpath(onlyAttrNames,onlyAttrValues, xpath, local_name, text, class_name, image, link, parent_name);
            }, false);
            """
        return Template(js).render(name=self.name)

    @QtCore.pyqtSlot(str, str, str, str, str, str, str, str, str)
    def receive_xpath(self, attribute_names, attribute_values, xpath, local_name, text, class_name, image, link, parent_name):
        self.xpathClicked.emit(attribute_names, attribute_values, xpath, local_name, text, class_name, image, link, parent_name)


class QtBrowserWidget(QtWidgets.QWidget):

    def __init__(self, view, *args, **kwargs):
        super(QtBrowserWidget, self).__init__(*args, **kwargs)
        # self.scene = scene
        self.setLayout(QtWidgets.QVBoxLayout())
        # BROWSER
        # self.browser = QtWebEngineWidgets.QWebEngineView()
        self.browser = view
        self.page = WebEnginePage()

        self.xpath_helper = Helper("xpath_helper")
        self.xpath_helper.xpathClicked.connect(self.return_xpath)

        self.page.add_object(self.xpath_helper)
        self.browser.setPage(self.page)

        self.browser.urlChanged.connect(self.update_urlbar)
        # self.browser.loadFinished.connect(self.update_title)
        profile = self.page.profile().httpUserAgent()
        # print('page profile: ', profile)

        # BROWSER NAVIGATION BAR
        self.browsernavbar = QtWidgets.QWidget()
        self.browsernavbar.setLayout(QtWidgets.QHBoxLayout())
        self.browsernavbar.layout().setAlignment(QtCore.Qt.AlignHCenter)
        self.browsernavbar.layout().setContentsMargins(0, 0, 0, 0)
        self.browsernavbar.setFixedHeight(30)

        back_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'arrow-left.svg')), "Back", self)
        back_btn.clicked.connect(self.browser.back)
        self.browsernavbar.layout().addWidget(back_btn)

        next_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'arrow-right.svg')), "Forward", self)
        next_btn.clicked.connect(self.browser.forward)
        self.browsernavbar.layout().addWidget(next_btn)

        reload_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'arrow-clockwise.svg')), "Reload", self)
        reload_btn.clicked.connect(self.browser.reload)
        self.browsernavbar.layout().addWidget(reload_btn)

        home_btn = QtWidgets.QPushButton(QtGui.QIcon(os.path.join('images', 'house-fill.svg')), "Home", self)
        home_btn.clicked.connect(self.navigate_home)
        self.browsernavbar.layout().addWidget(home_btn)

        self.httpsicon = QtWidgets.QLabel()
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('images', 'shield-lock-fill.svg')))
        self.browsernavbar.layout().addWidget(self.httpsicon)

        self.urlbar = QtWidgets.QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.browsernavbar.layout().addWidget(self.urlbar)

        self.layout().addWidget(self.browsernavbar)
        self.layout().addWidget(self.browser)
        self.browser.load(QtCore.QUrl(HOME))

    def navigate_home(self):
        self.browser.setUrl(QtCore.QUrl(HOME))

    def navigate_to_url(self):
        q = QtCore.QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

    def update_urlbar(self, q):
        if q.scheme() == 'https':
            self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('images', 'shield-lock-fill.svg')))
        else:
            self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('images', 'shield-slash.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def return_xpath(self, attribute_names, attribute_values, xpath, local_name, text, class_name, image, link, parent_name):

        if attribute_names or attribute_values:
            attributes = dict(zip(str(attribute_names).split(","), str(attribute_values).split(",")))
        else:
            attributes = None

        node_input = {
            'attributes': attributes,
            'text': text,
            'xpath': xpath
        }

        self.browser.value = node_input
        if DEBUG: print('BROWSER VALUE: ', self.browser.value)

    def inspect_element(self):
        if self.page.onLoadFinished:
            self.page.runJavaScript(
                """
            document.body.addEventListener('mouseenter', function(e) {
            e = e || window;
            const item = e.target;
            item.addEventListener('mouseover', function (event) {
                event.target.style.backgroundColor = '#21cdff';
            })
            item.addEventListener('mouseout', function (event) {
                event.target.style.backgroundColor = '';
            })
            }, false);
            """)


class QuteBrowser(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(QuteBrowser, self).__init__(*args, **kwargs)
        self.value = None

        self.scene = None
        # print('SELF.SCENE: ', self.scene)

        self.initNewNodeActions()

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(KELEBEK_NODES.keys())
        keys.sort()
        for key in keys:
            node = KELEBEK_NODES[key]
            self.node_actions[node.op_code] = QtWidgets.QAction(QtGui.QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QtWidgets.QMenu(self)
        keys = list(KELEBEK_NODES.keys())
        keys.sort()
        for key in keys: context_menu.addAction(self.node_actions[key])
        return context_menu

    # def initNodesContextMenu(self):
    #     context_menu = QtWidgets.QMenu(self)
    #     self.createContextMenu(context_menu, KELEBEK_NODES2)
    #     # keys = list(KELEBEK_NODES.keys())
    #     # keys.sort()
    #     # for key in keys: context_menu.addAction(self.node_actions[key])
    #     return context_menu

    def createContextMenu(self, parent, values):  # tODO make sure only web related nodes are allowed in the browser
        if isinstance(values, dict):
            for key, value in values.items():
                # NODES:
                if isinstance(key, int):
                    node = value
                    action = QtWidgets.QAction(QtGui.QIcon(node.icon), node.op_title)
                    action.setData(node.op_code)
                    parent.addAction(action)
                else:
                    menu = QtWidgets.QMenu(key)
                    parent.addMenu(menu)
                    self.createContextMenu(menu, value)

    def handleNewNodeContextMenu(self, event):
        import random
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        x = random.randrange(-200, 200, 20)
        y = random.randrange(-200, 200, 20)

        if action is not None:
            if self.scene is not None:
                new_kelebek_node = get_class_from_opcode(action.data())(self.scene)
                new_kelebek_node.setPos(x, y)
                try:
                    print('Node Value: ', self.value)
                    text = new_kelebek_node.xpath_operation(**self.value)
                    new_kelebek_node.content.edit.setText(text)
                except Exception as e:
                    print('Error inserting text.', e)
                self.scene.history.storeHistory("Created %s" % new_kelebek_node.__class__.__name__)
            else:
                print('SCENE IS NONE')

    def contextMenuEvent(self, event):
        # If there is not scene opened do not allow for context menu.
        if self.scene:
            self.handleNewNodeContextMenu(event)
        # else:
        #     super().contextMenuEvent(event)

