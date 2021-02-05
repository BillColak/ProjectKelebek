from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets, QtWebChannel
from jinja2 import Template
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

HOME = 'https://www.google.com/'


class Element(QtCore.QObject):
    def __init__(self, name, parent=None):
        super(Element, self).__init__(parent)
        self._name = name  # = 'xpath_helper'

    @property
    def name(self):
        return self._name

    def script(self):
        return ""


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
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
            channel = QtWebChannel.QWebChannel(self)
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
                e.preventDefault();
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
    def receive_xpath(self, names, values, xpath, local_name, text, class_name, image, link, parent_name):
        self.xpathClicked.emit(names, values, xpath, local_name, text, class_name, image, link, parent_name)


class QtBrowser(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(QtBrowser, self).__init__(*args, **kwargs)

    # def browser(self):
    #     self.browserwindow = QtWidgets.QWidget()
    #     self.browserwindow.setLayout(QtWidgets.QVBoxLayout())
        self.setLayout(QtWidgets.QVBoxLayout())
        # BROWSER
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.page = WebEnginePage()

        self.xpath_helper = Helper("xpath_helper")
        self.xpath_helper.xpathClicked.connect(self.return_xpath)

        self.page.add_object(self.xpath_helper)
        self.browser.setPage(self.page)

        self.browser.urlChanged.connect(self.update_urlbar)
        # self.browser.loadFinished.connect(self.update_title)
        profile = self.page.profile().httpUserAgent()
        print(profile)
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

        # self.browserwindow.layout().addWidget(self.browsernavbar)
        # self.browserwindow.layout().addWidget(self.browser)
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

    def return_xpath(self, names, values, xpath, local_name, text, class_name, image, link, parent_name):
        print(names, values, xpath, local_name, text, class_name, image, link, parent_name)
        return names, values, xpath, local_name, text, class_name, image, link, parent_name

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