# Under MIT License, see LICENSE.txt

from signal import signal, SIGINT

from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from Model.FrameModel import FrameModel
from Model.DataInModel import DataInModel
from Model.DataOutModel import DataOutModel
from Model.RecorderModel import RecorderModel

from View.FieldView import FieldView
from View.FilterCtrlView import FilterCtrlView
from View.StrategyCtrView import StrategyCtrView
from View.LoggerView import LoggerView
from View.MainWindow import MainWindow
from View.ParamView import ParamView
from View.MediaControllerView import MediaControllerView
from View.StatusBarView import StatusBarView
from View.GameStateView import GameStateView

from Communication.UDPServer import UDPServer
from Communication.vision import Vision

from .DrawingObjectFactory import DrawingObjectFactory
from .QtToolBox import QtToolBox

__author__ = 'RoboCupULaval'


class MainController(QWidget):
    # TODO: Dissocier Controller de la fenêtre principale
    def __init__(self):
        super().__init__()

        # Création des Contrôleurs
        self.draw_handler = DrawingObjectFactory(self)

        # Communication
        # self.network_data_in = UDPServer(self)
        self.network_data_in = UDPServer(name='UDPServer', debug=False)
        self.network_vision = Vision()
        self.ai_server_is_serial = False

        # Création des Modèles
        self.model_frame = FrameModel(self)
        self.model_datain = DataInModel(self)
        self.model_dataout = DataOutModel(self)
        self.model_recorder = RecorderModel()

        # Création des Vues
        self.main_window = MainWindow()
        self.view_menu = QMenuBar(self)
        self.view_logger = LoggerView(self)
        self.view_screen = FieldView(self)
        self.view_filter = FilterCtrlView(self)
        self.view_param = ParamView(self)
        self.view_controller = StrategyCtrView(self)
        self.view_media = MediaControllerView(self)
        self.view_status = StatusBarView(self)
        self.view_robot_state = GameStateView(self)

        # Initialisation des UI
        self.init_main_window()
        self.init_menubar()
        self.init_signals()

    def init_main_window(self):
        # Initialisation de la fenêtre
        self.setWindowTitle('RoboCup ULaval | GUI Debug')
        self.setWindowIcon(QIcon('Img/favicon.jpg'))
        self.resize(975, 750)

        # Initialisation des Layouts
        # => Field | Filter | StratController (Horizontal)
        sub_layout = QHBoxLayout()
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.addWidget(self.view_screen)
        sub_layout.addWidget(self.view_filter)
        sub_layout.addWidget(self.view_controller)

        # => Menu | SubLayout | Media | Logger | Status (Vertical)
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.view_menu)
        top_layout.addLayout(sub_layout)
        top_layout.addWidget(self.view_media)
        top_layout.addWidget(self.view_robot_state)
        top_layout.addWidget(self.view_logger)
        top_layout.addWidget(self.view_status)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setMargin(0)

        self.setLayout(top_layout)

        # Initialisation des modèles aux vues
        self.view_logger.set_model(self.model_datain)
        self.model_datain.setup_udp_server(self.network_data_in)
        self.model_dataout.setup_udp_server(self.network_data_in)
        self.model_frame.set_vision(self.network_vision)
        self.model_frame.start()
        self.model_frame.set_recorder(self.model_recorder)
        self.model_datain.set_recorder(self.model_recorder)

    def init_menubar(self):
        # Titre des menus et dimension
        self.view_menu.setFixedHeight(30)
        fileMenu = self.view_menu.addMenu('Fichier')
        viewMenu = self.view_menu.addMenu('Affichage')
        toolMenu = self.view_menu.addMenu('Outil')
        helpMenu = self.view_menu.addMenu('Aide')

        # Action et entête des sous-menus
        # => Menu Aide
        helpAction = QAction('À propos', self)
        helpAction.triggered.connect(self.aboutMsgBox)
        helpMenu.addAction(helpAction)

        # => Menu Fichier

        paramAction = QAction('Paramètres', self)
        paramAction.triggered.connect(self.view_param.show)
        fileMenu.addAction(paramAction)

        fileMenu.addSeparator()

        exitAction = QAction('Quitter', self)
        exitAction.triggered.connect(self.closeEvent)
        fileMenu.addAction(exitAction)

        # => Menu Vue
        fieldMenu = viewMenu.addMenu('Terrain')

        toggleFrameRate = QAction("Afficher/Cacher la fréquence", self, checkable=True)
        toggleFrameRate.triggered.connect(self.view_screen.toggle_frame_rate)
        fieldMenu.addAction(toggleFrameRate)

        fieldMenu.addSeparator()

        flipXAction = QAction("Changer l'axe des X", self, checkable=True)
        flipXAction.triggered.connect(self.flip_screen_x_axe)
        fieldMenu.addAction(flipXAction)

        flipYAction = QAction("Changer l'axe des Y", self, checkable=True)
        flipYAction.triggered.connect(self.flip_screen_y_axe)
        fieldMenu.addAction(flipYAction)

        viewMenu.addSeparator()

        camMenu = viewMenu.addMenu('Camera')

        resetCamAction = QAction("Réinitialiser la caméra", self)
        resetCamAction.triggered.connect(self.view_screen.reset_camera)
        camMenu.addAction(resetCamAction)

        lockCamAction = QAction("Bloquer la caméra", self)
        lockCamAction.triggered.connect(self.view_screen.toggle_lock_camera)
        camMenu.addAction(lockCamAction)

        viewMenu.addSeparator()

        botMenu = viewMenu.addMenu('Robot')

        vanishAction = QAction('Afficher Vanishing', self, checkable=True)
        vanishAction.triggered.connect(self.view_screen.toggle_vanish_option)
        botMenu.addAction(vanishAction)

        vectorAction = QAction('Afficher Vecteur vitesse des robots', self, checkable=True)
        vectorAction.triggered.connect(self.view_screen.toggle_vector_option)
        botMenu.addAction(vectorAction)

        nuumbAction = QAction('Afficher Numéro des robots', self, checkable=True)
        nuumbAction.triggered.connect(self.view_screen.show_number_option)
        botMenu.addAction(nuumbAction)

        viewMenu.addSeparator()

        fullscreenAction = QAction('Fenêtre en Plein écran', self, checkable=True)
        fullscreenAction.triggered.connect(self.toggle_full_screen)
        fullscreenAction.setShortcut(Qt.Key_F2)
        viewMenu.addAction(fullscreenAction)

        # => Menu Outil
        filterAction = QAction('Filtre pour dessins', self, checkable=True)
        filterAction.triggered.connect(self.view_filter.show_hide)
        toolMenu.addAction(filterAction)

        StrategyControllerAction = QAction('Contrôleur de Stratégie', self,  checkable=True)
        StrategyControllerAction.triggered.connect(self.view_controller.toggle_show_hide)
        toolMenu.addAction(StrategyControllerAction)

        toolMenu.addSeparator()

        mediaAction = QAction('Contrôleur Média', self, checkable=True)
        mediaAction.triggered.connect(self.view_media.toggle_visibility)
        toolMenu.addAction(mediaAction)

        robStateAction = QAction('État des robots', self, checkable=True)
        robStateAction.triggered.connect(self.view_robot_state.show_hide)
        toolMenu.addAction(robStateAction)

        loggerAction = QAction('Loggeur', self,  checkable=True)
        loggerAction.triggered.connect(self.view_logger.show_hide)
        toolMenu.addAction(loggerAction)

    def init_signals(self):
        signal(SIGINT, self.signal_handle)
        self.connect(self, SIGNAL('triggered()'), self.closeEvent)

    def update_logging(self):
        self.view_logger.refresh()

    def save_logging(self, path, texte):
        self.model_datain.write_logging_file(path, texte)

    def aboutMsgBox(self):
        QMessageBox.about(self, 'À Propos', 'ROBOCUP ULAVAL © 2016\n\ncontact@robocupulaval.com')

    def closeEvent(self, event):
        self.close()

    def signal_handle(self, *args):
        """ Responsable du traitement des signaux """
        self.close()

    def resize_window(self):
        # self.setFixedSize(self.minimumSizeHint())
        pass

    def add_draw_on_screen(self, draw):
        """ Ajout un dessin sur la fenêtre du terrain """
        try:
            qt_draw = self.draw_handler.get_qt_draw_object(draw)
            if qt_draw is not None:
                self.view_screen.load_draw(qt_draw)
        except:
            pass

    def set_ball_pos_on_screen(self, x, y):
        """ Modifie la position de la balle sur le terrain """
        self.view_screen.set_ball_pos(x, y)

    def set_robot_pos_on_screen(self, bot_id, pst, theta):
        """ Modifie la position et l'orientation d'un robot sur le terrain """
        self.view_screen.set_bot_pos(bot_id, pst[0], pst[1], theta)

    def hide_mob(self, bot_id=None):
        """ Cache l'objet mobile si l'information n'est pas update """
        if self.view_screen.isVisible() and not self.view_screen.option_vanishing:
            if bot_id is None:
                self.view_screen.hide_ball()
            else:
                self.view_screen.hide_bot(bot_id)

    def update_target_on_screen(self):
        """ Interruption pour mettre à jour les données de la cible """
        try:
            self.view_screen.auto_toggle_visible_target()
        except:
            pass

    def add_logging_message(self, name, message, level=2):
        """ Ajoute un message de logging typé """
        self.model_datain.add_logging(name, message, level=level)

    def get_drawing_object(self, index):
        """ Récupère un dessin spécifique """
        return self.draw_handler.get_specific_draw_object(index)

    def toggle_full_screen(self):
        """ Déclenche le plein écran """
        if not self.windowState() == Qt.WindowFullScreen:
            self.setWindowState(Qt.WindowFullScreen)
        else:
            self.setWindowState(Qt.WindowActive)

    def flip_screen_x_axe(self):
        """ Bascule l'axe des X de l'écran """
        QtToolBox.field_ctrl.flip_x_axe()

    def flip_screen_y_axe(self):
        """ Bascule l'axe des Y de l'écran """
        QtToolBox.field_ctrl.flip_y_axe()

    def get_list_of_filters(self):
        """ Récupère la liste des filtres d'affichage """
        name_filter = list(self.view_screen.draw_filterable.keys())
        name_filter += list(self.view_screen.multiple_points_map.keys())
        name_filter = set(name_filter)
        name_filter.add('None')
        return name_filter

    def set_list_of_filters(self, list_filter):
        """ Assigne une liste de filtres d'affichage """
        self.view_screen.list_filter = list_filter

    def deselect_all_robots(self):
        """ Désélectionne tous les robots sur le terrain """
        self.view_screen.deselect_all_robots()

    def select_robot(self, index, is_yellow):
        """ Sélectionne le robot spécifié par l'index sur le terrain """
        self.view_screen.select_robot(index, is_yellow)

    def get_tactic_controller_is_visible(self):
        """ Requête pour savoir le l'onglet de la page tactique est visible """
        return self.view_controller.page_tactic.isVisible()

    def force_tactic_controller_select_robot(self, index):
        """ Force le sélection du robot indiqué par l'index dans la combobox du contrôleur tactique """
        if index > 5:
            self.view_controller.selectTeam.setCurrentIndex(1)
            self.view_controller.selectRobot.setCurrentIndex(index - 6)
        else:
            self.view_controller.selectTeam.setCurrentIndex(0)
            self.view_controller.selectRobot.setCurrentIndex(index)

    def get_cursor_position_from_screen(self):
        """ Récupère la position du curseur depuis le terrain """
        x, y = self.view_screen.get_cursor_position()
        coord_x, coord_y = QtToolBox.field_ctrl.convert_screen_to_real_pst(x, y)
        return int(coord_x), int(coord_y)

    def toggle_recorder(self, p_bool):
        """ Active/Désactive le Recorder """
        if p_bool:
            self.model_frame.enable_recorder()
            self.model_datain.enable_recorder()
        else:
            self.model_frame.disable_recorder()
            self.model_datain.disable_recorder()

    def get_fps(self):
        """ Récupère la fréquence de rafraîchissement de l'écran """
        return self.view_screen.get_fps()

    def get_is_serial(self):
        """ Récupère si le serveur de strategyIA est en mode serial (True) ou udp (False)"""
        return self.ai_server_is_serial

    def set_is_serial(self, is_serial):
        """ Détermine si le serveur de strategyIA est en mode serial (True) ou udp (False)"""
        self.ai_server_is_serial = is_serial

    def send_handshake(self):
        """ Envoie un HandShake au client """
        self.model_dataout.send_handshake()

    def send_ports_rs(self):
        ports_info = dict(zip(['recv_port',
                               'send_port'],
                              [self.network_data_in.get_rcv_port(),
                               self.network_data_in.get_snd_port()]))
        self.model_dataout.send_ports_rs(ports_info)

    def send_server(self):
        """ Envoie si le serveur utilisé par strategyIA est en serial (True) ou en udp (False)"""
        server_info = dict(zip(['is_serial', 'ip', 'port'],
                               [self.ai_server_is_serial,
                                self.network_vision.get_ip(),
                                self.network_vision.get_port()]))
        self.model_dataout.send_server(server_info)

    def send_geometry(self):
        """ Envoie la géométrie du terrain """
        self.model_dataout.send_geometry(QtToolBox.field_ctrl)

    def waiting_for_robot_state(self):
        return self.model_datain.waiting_for_robot_state_event()

    def waiting_for_game_state(self):
        return self.model_datain.waiting_for_game_state_event()

    # === RECORDER METHODS ===
    def recorder_is_playing(self):
        return self.model_recorder.is_playing()

    def recorder_get_cursor_percentage(self):
        return self.model_recorder.get_cursor_percentage()

    def recorder_trigger_pause(self):
        self.model_recorder.pause()

    def recorder_trigger_play(self):
        self.model_recorder.play()

    def recorder_trigger_back(self):
        self.model_recorder.back()

    def recorder_trigger_rewind(self):
        self.model_recorder.rewind()

    def recorder_trigger_forward(self):
        self.model_recorder.forward()

    def recorder_skip_to(self, value):
        self.model_recorder.skip_to(value)

