# Under MIT License, see LICENSE.txt

from time import sleep
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt, QThread

__author__ = 'RoboCupULaval'


class MediaControllerView(QtGui.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Vue
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        button_layout = QtGui.QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self._media_slider = QtGui.QSlider(self)
        self.connect(self._media_slider, QtCore.SIGNAL('sliderReleased()'),
                     self, QtCore.SLOT('sliderReleased()'))
        self.connect(self._media_slider, QtCore.SIGNAL('sliderMoved()'),
                     self, QtCore.SLOT('sliderMoved()'))
        self._media_slider.setPageStep(1)
        self._media_slider.setOrientation(Qt.Horizontal)
        self._media_slider.setMaximumWidth(500)

        layout.addLayout(button_layout)
        layout.addWidget(self._media_slider)

        self._but_play = QtGui.QPushButton(QtGui.QIcon('Img/control_play.png'), '')
        self._but_play.clicked.connect(self.play)
        self._but_play.setFixedSize(20, 20)
        self._but_pause = QtGui.QPushButton(QtGui.QIcon('Img/control_pause.png'), '')
        self._but_pause.clicked.connect(self.pause)
        self._but_pause.setFixedSize(20, 20)
        self._but_rewind = QtGui.QPushButton(QtGui.QIcon('Img/control_rewind.png'), '')
        self._but_rewind.clicked.connect(self.rewind)
        self._but_rewind.setFixedSize(20, 20)
        self._but_back = QtGui.QPushButton(QtGui.QIcon('Img/control_start.png'), '')
        self._but_back.clicked.connect(self.back)
        self._but_back.setFixedSize(20, 20)
        self._but_forward = QtGui.QPushButton(QtGui.QIcon('Img/control_end.png'), '')
        self._but_forward.clicked.connect(self.forward)
        self._but_forward.setFixedSize(20, 20)

        button_layout.addWidget(self._but_rewind)
        button_layout.addWidget(self._but_back)
        button_layout.addWidget(self._but_play)
        button_layout.addWidget(self._but_pause)
        button_layout.addWidget(self._but_forward)

        self._thread = QThread()
        self._thread.run = self.update_slider
        self._thread.start()

        self.hide()

    def update_slider(self):
        while True:
            if self.controller.model_recorder._ctrl_play:
                self._media_slider.setValue(self.controller.model_recorder.get_cursor_percentage())
            sleep(0.1)

    def pause(self):
        self.controller.model_recorder.pause()
        self._media_slider.setValue(self.controller.model_recorder.get_cursor_percentage())
        self._media_slider.setDisabled(False)

    def play(self):
        self.controller.model_recorder.play()
        self._media_slider.setDisabled(True)

    def back(self):
        self.controller.model_recorder.back()
        self._media_slider.setValue(self.controller.model_recorder.get_cursor_percentage())

    def rewind(self):
        self.controller.model_recorder.rewind()
        self._media_slider.setValue(self.controller.model_recorder.get_cursor_percentage())

    def forward(self):
        self.controller.model_recorder.forward()
        self._media_slider.setValue(self.controller.model_recorder.get_cursor_percentage())

    @QtCore.pyqtSlot()
    def sliderReleased(self):
        self.controller.model_recorder.skip_to(self._media_slider.value())

    @QtCore.pyqtSlot()
    def sliderMoved(self):
        print('YO')
        self.controller.model_recorder.skip_to(self._media_slider.value())

    def toggle_visibility(self):
        if self.isVisible():
            self.play()
            self.hide()
        else:
            self.pause()
            self.show()

    def show(self):
        self.controller.toggle_recorder(True)
        super().show()

    def hide(self):
        self.controller.toggle_recorder(False)
        super().hide()
