# Under MIT License, see LICENSE.txt

from Model.DataObject.BaseDataObject import catch_format_error
from Model.DataObject.DrawingData.BaseDataDraw import BaseDataDraw

__author__ = 'RoboCupULaval'


class DrawMultipleLinesDataIn(BaseDataDraw):
    def __init__(self, data_in):
        super().__init__(data_in)
        self._format_data()

    @catch_format_error
    def _check_obligatory_data(self):
        """ Vérifie les données obligatoires """
        assert isinstance(self.data, dict),\
            "data: {} n'est pas un dictionnaire.".format(type(self.data))
        keys = self.data.keys()
        assert 'points' in keys, "data['points'] n'existe pas."
        assert isinstance(self.data['points'], list), "data['points'] n'est pas une liste."
        for point in self.data['points']:
            assert self._point_is_valid(point), "data['points']: {} n'est pas un point valide.".format(point)

    @catch_format_error
    def _check_optional_data(self):
        """ Vérifie les données optionnelles """
        keys = self.data.keys()
        if 'color' in keys:
            assert self._colorRGB_is_valid(self.data['color']), \
                "data['color']: {} n'est pas une couleur valide.".format(self.data['color'])
        else:
            self.data['color'] = (0, 0, 0)

        if 'width' in keys:
            assert 0 < self.data['width'], \
                "data['width']: {} n'est pas une épaisseur valide".format(self.data['width'])
        else:
            self.data['width'] = 2

        if 'style' in keys:
            assert self.data['style'] in self.line_style_allowed, \
                "data['style']: {} n'est pas une style valide".format(self.data['style'])
        else:
            self.data['style'] = 'SolidLine'

        if 'timeout' in keys:
            assert self.data['timeout'] >= 0, \
                "data['timeout']: {} n'est pas valide.".format(self.data['timeout'])
        else:
            self.data['timeout'] = 0

    @staticmethod
    def get_default_data_dict():
        return dict(zip(['points'],
                        [[(x * 100, 50) for x in range(5)]]))

    @staticmethod
    def get_type():
        return 3002
