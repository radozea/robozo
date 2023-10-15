import sys
import os
import requests
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QLabel, QTabWidget, QListWidget, QMessageBox, QCompleter, QAction, QTextBrowser, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineDownloadItem


class DownloadManager:
    def __init__(self, parent):
        self.parent = parent
        self.downloads_list = QListWidget()

    def download_requested(self, download_item):
        download_item.finished.connect(self.download_finished)
        self.downloads_list.addItem(download_item.url().fileName())
        download_item.accept()

    def download_finished(self):
        download_item = self.parent.sender()
        self.downloads_list.addItem(download_item.url().fileName())
        QMessageBox.information(self.parent, "Download Complete", f"Downloaded: {download_item.url().fileName()}")


class HistoryTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_url)

        layout = QVBoxLayout()
        layout.addWidget(self.history_list)
        self.setLayout(layout)

        # Load browsing history
        self.load_history()

    def update_history(self, url):
        self.history_list.addItem(url.toString())
        self.save_history()

    def load_url(self, item):
        url = item.text()
        self.parent.view.load(QUrl(url))

    def save_history(self):
        with open(".history.txt", "w") as file:
            for index in range(self.history_list.count()):
                url = self.history_list.item(index).text()
                file.write(url + "\n")

    def load_history(self):
        if os.path.exists(".history.txt"):
            with open(".history.txt", "r") as file:
                for line in file:
                    url = line.strip()
                    self.history_list.addItem(url)


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.settings_label = QLabel("UNDER CONSTRUCTION", alignment=Qt.AlignCenter)
        self.settings_label.setStyleSheet("font-size: 18px;")

        layout = QVBoxLayout()
        layout.addWidget(self.settings_label)
        self.setLayout(layout)


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()

        self.about_text = QTextBrowser()
        self.about_text.setOpenExternalLinks(True)
        self.about_text.setHtml("<h2>About Zenith Web Browser</h2>"
                                "<p>Zenith Web Browser is a simple web browser built using PyQt5 and "
                                "PyQtWebEngine. It provides a tabbed browsing experience and basic "
                                "web browsing functionalities. Enjoy surfing the web with Zenith!</p>"
                                "<p>Author: Zeke aka gamedev2084</p>")

        layout = QVBoxLayout()
        layout.addWidget(self.about_text)
        self.setLayout(layout)


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Zenith Web Browser")
        self.setGeometry(100, 100, 800, 600)

        self.view = QWebEngineView()
        self.view.load(QUrl("https://www.google.com"))
        self.view.loadFinished.connect(self.update_address_bar)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)

        self.history_tab = HistoryTab(self)

        self.settings_tab = SettingsTab()

        self.downloads_tab = QWidget()
        self.downloads_tab_layout = QVBoxLayout(self.downloads_tab)
        self.downloads_manager = DownloadManager(self)
        self.downloads_tab_layout.addWidget(self.downloads_manager.downloads_list)

        self.about_tab = AboutTab()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.view, "Browser")
        self.tab_widget.addTab(self.history_tab, "History")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.downloads_tab, "Downloads")
        self.tab_widget.addTab(self.about_tab, "About")

        self.forward_button = QPushButton("▷")
        self.forward_button.setStyleSheet(
            """
            QPushButton {
                font-size: 23px;
                border: none;
                padding: 0;
                margin: 0;
                background-color: transparent;
            }

            QPushButton:hover {
                background-color: #ebebeb;
            }
            """
        )
        self.forward_button.setMaximumSize(30, 30)

        self.back_button = QPushButton("◁")
        self.back_button.setStyleSheet(
            """
            QPushButton {
                font-size: 23px;
                border: none;
                padding: 0;
                margin: 0;
                background-color: transparent;
            }

            QPushButton:hover {
                background-color: #ebebeb;
            }
            """
        )
        self.back_button.setMaximumSize(30, 30)

        self.reload_button = QPushButton("↻")
        self.reload_button.setStyleSheet(
            """
            QPushButton {
                font-size: 23px;
                border: none;
                padding: 0;
                margin: 0;
                background-color: transparent;
            }

            QPushButton:hover {
                background-color: #ebebeb;
            }
            """
        )
        self.reload_button.setMaximumSize(30, 30)

        address_layout = QHBoxLayout()
        address_layout.addWidget(self.back_button)
        address_layout.addWidget(self.forward_button)
        address_layout.addWidget(self.reload_button)
        address_layout.addWidget(self.address_bar)

        address_widget = QWidget()
        address_widget.setLayout(address_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(address_widget)
        main_layout.addWidget(self.tab_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set up download manager
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.downloads_manager.download_requested)

        # Create actions for history
        self.clear_history_action = QAction("Clear History", self)
        self.clear_history_action.triggered.connect(self.clear_history)

        # Download and set the application icon/logo
        self.download_logo()

        # Connect button signals
        self.forward_button.clicked.connect(self.go_forward)
        self.back_button.clicked.connect(self.go_back)
        self.reload_button.clicked.connect(self.reload_page)

    def load_url(self):
        url = self.address_bar.text()
        if url.startswith(("c:/", "file:///")):
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "HTML Files (*.html *.htm)")
            if file_path:
                url = QUrl.fromLocalFile(file_path)
            else:
                return
        else:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            url = QUrl(url)

        self.view.load(url)

    def update_address_bar(self):
        self.address_bar.setText(self.view.url().toString())
        self.history_tab.update_history(self.view.url())

    def update_completer(self, text):
        suggestions = [
            "https://www.google.com",
            "https://www.yahoo.com",
            "https://www.bing.com",
            "https://www.duckduckgo.com",
            "https://www.wikipedia.org",
        ]
        completer = self.address_bar.completer()
        completer.setModel(completer.model().stringList())
        completer.setModelSorting(QCompleter.CaseSensitivelySortedModel)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionPrefix(text)

    def clear_history(self):
        self.history_tab.history_list.clear()
        self.history_tab.save_history()

    def download_logo(self):
        url = "https://img.icons8.com/?size=512&id=56925&format=png"
        response = requests.get(url)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.setWindowIcon(QIcon(pixmap))
        else:
            print("Failed to download the logo.")

    def go_forward(self):
        if self.view.history().canGoForward():
            self.view.forward()

    def go_back(self):
        if self.view.history().canGoBack():
            self.view.back()

    def reload_page(self):
        self.view.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WebBrowser()
    browser.show()
    sys.exit(app.exec_())
