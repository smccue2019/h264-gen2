from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class JDS_generator(QThread):

    new_jds = pyqtSignal(str, name = 'new_jds')
    
    def __init__(self):
        QThread.__init__(self)

        self.jdsheartbeat = QTimer()
        self.jdsheartbeat.timeout.connect(self.on_jdsheartbeat)
        self.jdsheartbeat.start(1000)

    def on_jdsheartbeat(self):

        jds = "JDS 2012/04/13 16:52:39 JAS2 11.68 -58.54 851.68 6020.31 0.0 -3.2 2 44.02 1327.99 0.81 24356.0 -0.5"
        self.new_jds.emit(jds)

class ODR_generator(QThread):

    new_odr = pyqtSignal(str, name = 'new_odr')

    def __init__(self):
        QThread.__init__(self)
        
        self.odfheartbeat = QTimer()
        self.odrheartbeat.timeout.connect(self.on_odrheartbeat)
        self.odrheartbeat.start(9000)

    def on_odrheartbeat(self):

        odr = "ODR 20120413 165239 JAS2 1.0 2.0 11 N001_McCue12 J2-000"

        self.new_odr.emit(odr)

class DPA_generator(QThread):

    new_dpa = pyqtSignal(str, name = 'new_dpa')

    def __init__(self, flag_preset=True):
        QThread.__init__(self)

        # Bottom lock flag based on passed preset
        if flag_preset:
            self.odr = "DPA 2022/04/21 01:00:09.463 JAS 7.9 1"
        else:
            self.odr = "DPA 2022/04/21 01:00:09.463 JAS 7.9 0"
            
        self.dpaheartbeat = QTimer()
        self.dpaheartbeat.timeout.connect(self.on_dpaheartbeat)
        self.dpaheartbeat.start(1000)

    def on_dpaheartbeat(self):
        self.new_odr.emit(self.odr)
