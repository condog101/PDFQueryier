# # Only needed for access to command line arguments
# import sys

#         # IMPORTANT!!!!! Windows are hidden by default.


# # You need one (and only one) QApplication instance per application.
# # Pass in sys.argv to allow command line arguments for your app.
# # If you know you won't use command line arguments QApplication([]) works too.
# app = QApplication(sys.argv)

# # Create a Qt widget, which will be our window.
# window = MainWindow()


import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from file_displayer import Drive
from ai import SmartDoc


class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)


class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # Generate the structure parts of the MainWindow
        self.thread_manager = QThreadPool()
        self.central_widget = QWidget()  # A QWidget to work as Central Widget
        self.layout1 = QVBoxLayout()  # Vertical Layout
        self.layout2 = QHBoxLayout()  # Horizontal Layout
        drive = Drive()
        self.doc = SmartDoc()
        self.widget_one = WidgetOne(drive.files)
        self.widget_two = WidgetTwo()

        self.title = QLabel('Paper Querier:')
        self.layout1.addWidget(self.title)

        # Build the structure
        # Insert a QWidget as a central widget for the MainWindow
        self.setCentralWidget(self.central_widget)
        # Add a principal layout for the widgets/layouts you want to add
        self.central_widget.setLayout(self.layout1)
        # Add widgets/layuts, as many as you want, remember they are in a Vertical
        # layout: they will be added one below of the other
        self.layout1.addLayout(self.layout2)
        # Here we add the widgets to the horizontal layout: one next to the other
        self.layout1.addWidget(self.widget_one)
        self.layout2.addWidget(self.widget_two)
        # Connect the signal
        self.widget_two.submitClicked.connect(self.on_click)

    @Slot()
    def on_click(self, feed):
        # Change the properties of the elements in the second widget

        source = self.widget_one.selected_option()
        query = feed[0]
        res = self.doc.get_result(query, source=source)

        text = res['data']['Get']['GoodDocument'][0]['_additional']['generate']['groupedResult']

        self.widget_two.label.setText(text)

# Build your widgets same as the Main Window, with the excepton that here you don't
# need a central widget, because it is already a widget.


class WidgetOne(QWidget):
    def __init__(self, options, parent=None):
        super(WidgetOne, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel('Select your file:')
        self.layout.addWidget(self.label)
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(options)
        self.combo_box.currentIndexChanged.connect(self.on_selection_changed)
        self.layout.addWidget(self.combo_box)

    def on_selection_changed(self, index):
        selected_option = self.combo_box.itemText(index)
        self.combo_box.setCurrentText(selected_option)

    def selected_option(self):
        return self.combo_box.currentText()


class WidgetTwo(QWidget):
    submitClicked = Signal([list])

    def __init__(self):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.sub_title = QLabel('Enter your prompt:')
        self.layout.addWidget(self.sub_title)

        self.line_edit = QLineEdit()
        self.layout.addWidget(self.line_edit)

        self.submit_button = QPushButton(text='Submit Prompt')
        self.submit_button.clicked.connect(self.on_button_clicked)
        self.layout.addWidget(self.submit_button)

        self.label = ScrollLabel()
        self.layout.addWidget(self.label)

    def fetch_input_text(self):
        return self.line_edit.text()

    def on_button_clicked(self):

        self.submitClicked.emit([self.fetch_input_text()])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
