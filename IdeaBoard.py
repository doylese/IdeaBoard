import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
                             QTextEdit, QInputDialog, QHBoxLayout, QMenu, QAction, QMessageBox, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QSizePolicy)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt


class Section(QWidget):
    def __init__(self, title):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel(title)
        self.title.setObjectName("sectionTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)


class IdeaBoard(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.sections = {}
        self.setupUI()

    def setupUI(self):
        self.addButton = QPushButton('Add New Idea')
        self.addButton.clicked.connect(self.addNewIdea)
        self.mainLayout.addWidget(self.addButton)

        self.addSectionButton = QPushButton('Add New Section')
        self.addSectionButton.clicked.connect(lambda: self.addNewSection())
        self.mainLayout.addWidget(self.addSectionButton)

    def addNewSection(self, sectionName=None):
        # Adding a guard clause for when the function might be receiving a boolean directly
        if isinstance(sectionName, bool):
            print("addNewSection was directly given a boolean value, which is unexpected.")
            return

        if sectionName is None:  # Only ask the user for a section name if one wasn't provided
            sectionName, ok = QInputDialog.getText(self, 'New Section', 'Enter section name:')
            if not ok or not sectionName:  # User cancelled or entered nothing
                print("Section creation cancelled by the user or received an empty name.")
                return

        if sectionName in self.sections:
            QMessageBox.warning(self, "Section Exists", "A section with this name already exists.")
            return

        try:
            section = Section(sectionName)  # We now know sectionName is not None or a boolean
            self.sections[sectionName] = section
            self.mainLayout.addWidget(section)
        except Exception as e:
            print(f"Error adding new section: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add new section: {e}")

    def addNewIdea(self):


        if not self.sections:
            self.addNewSection()
            if not self.sections:
                return


        ideaType, ok = QInputDialog.getItem(self, "Select Idea Type",
                                            "Choose the type of idea you want to add. This should take only a second to load: ",
                                            ["Text", "Image"], 0, False)
        if ok and ideaType:
            sectionName, ok = QInputDialog.getItem(self, "Select Section", "Choose the section:",
                                                   list(self.sections.keys()), 0, False)
            if ok and sectionName:
                if ideaType == "Text":
                    self.addTextIdea(sectionName)
                elif ideaType == "Image":
                    self.addImageIdea(sectionName)

    def addTextIdea(self, sectionName, text=None):
        if text is None:
            text, ok = QInputDialog.getText(self, 'Text', 'Enter your idea:')
            if not ok or text == '':
                return
        textWidget = QLabel(text)
        textWidget.setWordWrap(True)
        self.sections[sectionName].layout.addWidget(textWidget)

    def addImageIdea(self, sectionName, imagePath=None):

        if imagePath is None:
            imagePath, _ = QFileDialog.getOpenFileName(self, "Select image", "",
                                                       "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
            if not imagePath:
                return

        # Load the image and prepare the view
        pixmap = QPixmap(imagePath)
        scene = QGraphicsScene()
        pixmapItem = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmapItem)
        pixmapItem.setData(0, imagePath)  # Store the image path

        # Create and configure the view
        view = QGraphicsView(scene)
        view.setFixedSize(400, 400)
        view.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        view.setRenderHint(QPainter.Antialiasing)
        view.fitInView(pixmapItem, Qt.KeepAspectRatio)


        self.sections[sectionName].layout.addWidget(view)

    def serialize(self):
        board_data = {'name': self.name, 'sections': {}}
        for sectionName, sectionWidget in self.sections.items():
            section_data = []
            for i in range(sectionWidget.layout.count()):
                widget = sectionWidget.layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.objectName() != "sectionTitle":
                    section_data.append({'type': 'text', 'content': widget.text()})
                elif isinstance(widget, QGraphicsView):
                    items = widget.scene().items()
                    if items:
                        imagePath = items[0].data(0)
                        section_data.append({'type': 'image', 'content': imagePath})
            board_data['sections'][sectionName] = section_data
        return board_data

    def deserialize(self, data):
        # Clear current content
        self.clearBoard()


        for section_name, ideas in data['sections'].items():

            self.addNewSection(section_name)

            for idea in ideas:

                if idea['type'] == 'text':

                    self.addTextIdea(section_name, idea['content'])
                elif idea['type'] == 'image':

                    self.addImageIdea(section_name, idea['content'])

    def clearBoard(self):

        for section_name in list(self.sections.keys()):
            section_widget = self.sections[section_name]

            while section_widget.layout.count():
                item = section_widget.layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            # Now remove the section itself
            section_widget.deleteLater()
            del self.sections[section_name]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = IdeaBoard()
    mainWin.show()
    sys.exit(app.exec_())
