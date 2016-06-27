# Under MIT License, see LICENSE.txt

from Controller.BaseQtObject import BaseQtObject
from Controller.DrawQtObject.QtToolBox import QtToolBox
from Model.DataIn.DrawingDataIn.DrawCircleDataIn import DrawCircleDataIn
from PyQt4 import QtGui

__author__ = 'RoboCupULaval'


class CircleQtObject(BaseQtObject):

    @staticmethod
    def get_qt_item(drawing_data_in, screen_ratio=0.1, screen_width=9000, screen_height=6000):
        draw_data = drawing_data_in.data

        # Création du peintre
        pen = QtToolBox.create_pen(color=draw_data['color'],
                                   style=draw_data['style'],
                                   width=2)

        # Création de la brosse
        brush = QtToolBox.create_brush(color=draw_data['color'])

        # Création de l'objet
        x, y = draw_data['center']
        qt_objet = QtToolBox.create_ellipse_item(x - draw_data['radius'],
                                                 y - draw_data['radius'],
                                                 draw_data['radius'] * 2,
                                                 draw_data['radius'] * 2,
                                                 pen=pen,
                                                 is_fill=draw_data['is_fill'],
                                                 brush=brush,
                                                 opacity=1)
        qt_objet.setZValue(-1)
        return qt_objet

    @staticmethod
    def get_datain_associated():
        return DrawCircleDataIn.__name__