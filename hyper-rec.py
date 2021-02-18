#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
import configparser
from hyperdeck import Hyperdeck_driver
from sjm_pkg.HyperdeckRecUI import Ui_MainWindow
from sjm_pkg.time_routines import systime, systimef_s
from sjm_pkg.udp_receiver import UDPreceiver
from sjm_pkg.udp2subtitle import UDP2subtitle
from sjm_pkg.sim_udp import JDS_generator, ODR_generator

class HyperRecGUI(QMainWindow):

    def __init__(self, inifname,parent=None):
        super(HyperRecGUI, self).__init__(parent)

        # set up GUI, laid out using designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Turn off start button until an ODR packet comes in
        self.ui.startButton.setEnabled(False)
        # change buttin appearance also?
        self.ui.quitButton.clicked.connect(self.on_quit_button)
        self.ui.stopButton.clicked.connect(self.on_stop_button)
        self.ui.startButton.clicked.connect(self.on_start_button)

        self.do_init(inifname)
        
        # Allow simulate of UDP messges for debugging
        simulate_udp = True
        
        # Invoke classes for ingesting UDP broadcasts and writing subtitles
        # UDP2subtitle both logs subtitles to a file and generates
        # displayable strings. Three lines.

        self.subtitleGen = UDP2subtitle()
        self.meta_receiver=UDPreceiver(self.ListenPort)
        if (simulate_udp):
            self.jds_gen = JDS_generator()
            self.odr_gen = ODR_generator()
            self.jds_gen.new_jds.connect(self.on_new_jds)
            self.odr_gen.new_odr.connect(self.on_new_odr)
        else:
            self.meta_receiver.new_jds.connect(self.on_new_jds) 
            self.meta_receiver.new_odr.connect(self.on_new_odr)

        self.meta_receiver.new_jds.connect(self.subtitleGen.updateJDS)
        self.meta_receiver.new_odr.connect(self.subtitleGen.updateODR)

        self.deck1 = Hyperdeck_driver(self.hydeck1_IP, self.hydeck1_label, 2)
        self.deck2 = Hyperdeck_driver(self.hydeck2_IP, self.hydeck2_label, 2)
        self.deck3 = Hyperdeck_driver(self.hydeck3_IP, self.hydeck3_label, 2)

        self.deck1.deck_connected.connect(self.on_deck1_good_ping)
        self.deck2.deck_connected.connect(self.on_deck2_good_ping)
        self.deck3.deck_connected.connect(self.on_deck3_good_ping)
        
        self.deck1.clip_closed.connect(self.on_deck1_clip_closed)
        self.deck1.new_clip.connect(self.on_new_deck1_clip)
        self.deck2.clip_closed.connect(self.on_deck2_clip_closed)
        self.deck2.new_clip.connect(self.on_new_deck2_clip)
        self.deck3.clip_closed.connect(self.on_deck3_clip_closed)
        self.deck3.new_clip.connect(self.on_new_deck3_clip)

    def on_deck1_clip_closed(self, clipname):
        #self.subtitleGen.stop_logging()
        self.ui.clipGB_label.setText("Clip " + clipname + "closed at " + systime() )
        
    def on_new_deck1_clip(self, clipname):
        #self.subtitleGen.start_logging()
        self.cliptimecounter = 0
        self.ui.clipGB_label.setText("New clip started " + clipname )

    def on_deck2_clip_closed(self, clipname):
        self.subtitleGen.stop_logging()
        self.ui.clipGB_2_label.setText("Clip " + clipname + "closed at " + systime() )

    def on_new_deck2_clip(self, clipname):
        self.subtitleGen.start_logging()
        self.cliptimecounter = 0
        self.ui.clipGB_2_label.setText("New clip started " + clipname )

    def on_deck3_clip_closed(self, clipname):
        self.subtitleGen.stop_logging()
        self.ui.clipGB_3_label.setText("Clip " + clipname + "closed at " + systime() )

    def on_new_deck3_clip(self, clipname):
        #self.subtitleGen.start_logging()
        self.cliptimecounter = 0
        self.ui.clipGB_3_label.setText("New clip started " + clipname )

    def at_disp_systime_timeout(self):
        self.now = systime()
        self.now_f = systimef_s();
        self.ui.DateTimeDisp.setText(self.now_f)

    def on_new_jds(self, new_jds):
        #print(new_jds)
        self.subtitleGen.updateJDS(new_jds)
        self.ui.JDSflash.setStyleSheet("QLabel {background: green}")
        self.jdsflashtimer.start(self.flash_on_duration)

    def on_new_odr(self, new_odr):
        self.odr_has_been_received = True
        self.ui.startButton.setEnabled(True)
        self.subtitleGen.updateODR(new_odr)
        self.ui.ODRflash.setStyleSheet("QLabel {background: green}")
        self.odrflashtimer.start(self.flash_on_duration)

    def on_jdsflashtimer_timeout(self):
        self.ui.JDSflash.setStyleSheet("QLabel {background: white}")

    def on_odrflashtimer_timeout(self):
        self.ui.ODRflash.setStyleSheet("QLabel {background: white}")

    def on_deck1_good_ping(self, str):
        self.ui.clipGB_label.setStyleSheet("QLabel {background: light green}")

    def on_deck2_good_ping(self, str):
        self.ui.clipGB_2_label.setStyleSheet("QLabel {background: light green}")

    def on_deck3_good_ping(self, str):
        self.ui.clipGB_3_label.setStyleSheet("QLabel {background: light green}")

    def at_cliptimerheartbeat_timeout(self):
        self.cliptimecounter += 1
        self.ui.clipTimeLabel.setText(str(self.cliptimecounter))
        
    def do_init(self, inifname):
        #self.hydeck1_IP="198.17.154.97"
        #self.hydeck1_label="SciCam"
        #self.hydeck2_IP="198.17.154.98"
        #self.hydeck2_label="BrowCam"
        #self.hydeck3_IP="198.17.154.99"
        #self.hydeck3_label="PilotCam"
        #self.ListenPort=10502

        ip = configparser.ConfigParser()
        ip.read("hyper-rec.ini")

        self.hydeck1_IP=ip.get('NETWORK','hydeck1_IP')
        self.hydeck2_IP=ip.get('NETWORK','hydeck2_IP')
        self.hydeck3_IP=ip.get('NETWORK','hydeck3_IP')
        self.ListenPort=int(ip.get('NETWORK','ListenPort'))

        self.hydeck1_label=ip.get('DECK','hydeck1_label')
        self.hydeck2_label=ip.get('DECK','hydeck2_label')
        self.hydeck3_label=ip.get('DECK','hydeck3_label')
        
#        self.ID2GB = {
#            'clipGB':'SciCam',
#            'clipGB_2':'PilotCam',
#            'clipGB_3':'BrowCam'
#            }

        self.ID2GB = {
            'clipGB':self.hydeck1_label,
            'clipGB_2':self.hydeck2_label,
            'clipGB_3':self.hydeck3_label,
            }

        for key in self.ID2GB.keys():
            do = ( "self.ui."+key+".setTitle('"+self.ID2GB[key]+"')" )
            eval(do)

        self.odr_has_been_received = False            

        # Set up timers that define flash of a UI box upon receipt of
        # JDS and ODR packets. The flash is intiated by a signal from
        # UDPreceiver, the timer shuts down the flash.
        self.flash_on_duration = 200  # milliseconds
        self.odrflashtimer=QTimer()
        self.odrflashtimer.timeout.connect(self.on_odrflashtimer_timeout)
        self.jdsflashtimer=QTimer()
        self.jdsflashtimer.timeout.connect(self.on_jdsflashtimer_timeout)
        
        self.disp_systime_timer = QTimer()
        self.disp_systime_timer.timeout.connect(self.at_disp_systime_timeout)
        self.disp_systime_timer.start(1000)        

        self.clipTimeHeartbeatTimer = QTimer()
        self.clipTimeHeartbeatTimer.timeout.connect(self.at_cliptimerheartbeat_timeout)

    def on_start_button(self):
        if ( self.deck1.isInitiated() == False):
            self.deck1.manual_start()
            self.ui.clipGB.setStyleSheet("QGroupBox { border: 10px red;}")
        if ( self.deck2.isInitiated() == False):
            self.deck2.manual_start()
            self.ui.clipGB_2.setStyleSheet("QGroupBox { border: 10px red;}")
        if ( self.deck3.isInitiated() == False):
            self.deck3.manual_start()
            self.ui.clipGB_3.setStyleSheet("QGroupBox { border: 10px red;}")

        self.ui.recIconLabel.setStyleSheet("QLabel {background: red}")

        self.cliptimecounter = 0
        self.clipTimeHeartbeatTimer.start(1000)
        
    def on_stop_button(self):

        if ( self.deck1.isInitiated() == True):
            self.deck1.manual_stop()
            self.ui.clipGB.setStyleSheet("QGroupBox { border: 10px black;}")
        if ( self.deck2.isInitiated() == True):
            self.deck2.manual_stop()
            self.ui.clipGB_2.setStyleSheet("QGroupBox { border: 10px black;}")
        if ( self.deck3.isInitiated() == True):
            self.deck3.manual_stop()
            self.ui.clipGB_3.setStyleSheet("QGroupBox { border: 10px black;}")

        if ( self.subtitleGen.isInitiated() == True):
            self.subtitleGen.stop_logging()

        self.ui.recIconLabel.setStyleSheet("QLabel {background: black}")
        self.cliptimecounter = 0
        self.clipTimeHeartbeatTimer.stop()
        
    def on_quit_button(self):
        self.deck1.manual_stop()
        self.deck2.manual_stop()
        self.deck3.manual_stop()

        self.subtitleGen.stop_logging()
        QCoreApplication.exit()

    # def on_jds_receipt(self):
        
    # def set_status_green(self):
    #     self.ui.hypdeckGroupLeft.setStyleSheet("QGroupBox { border: 10px solid green;}")
    #     self.ui.hypdeckGroupMiddle.setStyleSheet("QGroupBox { border: 10px solid green;}")
    #     self.ui.hypdeckGroupRight.setStyleSheet("QGroupBox { border: 10px solid green;}")

    # def set_status_yellow(self):
    #     self.ui.hypdeckGroupLeft.setStyleSheet("QGroupBox { border: 10px solid yellow;}")
    #     self.ui.hypdeckGroupMiddle.setStyleSheet("QGroupBox { border: 10px solid yellow;}")
    #     self.ui.hypdeckGroupRight.setStyleSheet("QGroupBox { border: 10px solid yellow;}")

    # def set_status_red(self):
    #     self.ui.hypdeckGroupLeft.setStyleSheet("QGroupBox { border: 10px solid red;}")
    #     self.ui.hypdeckGroupMiddle.setStyleSheet("QGroupBox { border: 10px solid red;}")
    #     self.ui.hypdeckGroupRight.setStyleSheet("QGroupBox { border: 10px solid red;}")

if __name__ == "__main__":

    # Minor config here. User defines config filename.
    ini_filename = "hyper_rec.ini"

    app = QApplication(sys.argv)

    ini_filename="hyper_rec.ini"
    hr=HyperRecGUI(ini_filename)
    hr.show()
        
    sys.exit(app.exec_())


    # def on_ping_return(self, deckID):

    #     to_eval = ('self.ui.' + self.ID2GB[deckID] + '.setStyleSheet("QGroupBox { background-color: green; }")')   #border: 6px solid green;}")
    #     print(to_eval)

    # def on_transport_info_return(self, deckID, transport_info):

    #     for line in transport_info:
    #         (name, value) = line.split(': ', 1)
    #         self.status[name] = value

    #         if value == 'record':
    #             to_eval = ('self.ui.' + self.ID2GB[deckID] + '.setStyleSheet("QGroupBox { border: 6px solid green; }")')
    #         elif status == 'stop':
    #             to_eval = ('self.ui.' + self.ID2GB[deckID] + '.setStyleSheet("QGroupBox { border: 6px red; }")')
    #         else:
    #             continue
    #         print(to_eval)