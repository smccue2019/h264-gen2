from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class JDS_generator(QThread):

    new_jds = pyqtSignal(str, name = 'new_jds')
    
    def __init__(self):
        QThread.__init__(self)

        self.heartbeat = QTimer()
        self.heartbeat.timeout.connect(self.on_heartbeat)
        self.heartbeat.start(1000)

    def on_heartbeat(self):

        jds = "JDS 2012/04/13 16:52:39 JAS2 11.68 -58.54 851.68 6020.31 0.0 -3.2 2 44.02 1327.99 0.81 24356.0 -0.5"
        self.new_jds.emit(jds)

class ODR_generator(QThread):

    new_odr = pyqtSignal(str, name = 'new_odr')

    def __init__(self):
        QThread.__init__(self)
        
        self.heartbeat = QTimer()
        self.heartbeat.timeout.connect(self.on_heartbeat)
        self.heartbeat.start(9000)

    def on_heartbeat(self):

        odr = "ODR 20120413 165239 JAS2 1.0 2.0 11 N001_McCue12 J2-000"

        self.new_odr.emit(odr)
