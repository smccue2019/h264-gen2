#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys, logging, random
import configparser
from hyperdeck import Hyperdeck_driver
from sjm_pkg.HyperdeckRecUI import Ui_MainWindow
from sjm_pkg.time_routines import systime, systimef_s, systime_s, secs2ms
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

        myloggername = ("hrec_" + systime_s() + ".log")
        logging.basicConfig(filename=myloggername, level=logging.DEBUG)

        # change button appearance also?
        self.ui.quitButton.clicked.connect(self.on_quit_button)
        self.ui.stopButton.clicked.connect(self.on_stop_button)
        self.ui.startButton.clicked.connect(self.on_start_button)
        self.ui.estopButton.clicked.connect(self.on_estop_button)

        self.do_init(inifname)

        # Allow simulate of UDP messges for debugging
        # Normal operation, set simulate_udp to False 
        simulate_udp = False
        
        # Invoke classes for ingesting UDP broadcasts and writing subtitles
        # UDP2subtitle both logs subtitles to a file and generates
        # displayable strings. Three lines.

        self.subtitleGen = UDP2subtitle()
        self.subtitleGen.lowID.connect(self.on_new_lowID)
        self.subtitleGen.new_meta.connect(self.on_new_meta)
        self.subtitleGen.meta_closed.connect(self.on_meta_closed)
        #self.subtitleGen.new_dpa_locked(self.update
        
        self.meta_receiver=UDPreceiver(self.ListenPort)

        if (simulate_udp):
            self.jds_gen = JDS_generator()
            self.odr_gen = ODR_generator()
            self.dpa_gen = DPA_generator()
            self.jds_gen.new_jds.connect(self.on_new_jds)
            self.odr_gen.new_odr.connect(self.on_new_odr)
            self.odr_gen.new_dpa.connect(self.on_new_dpa)
        else:
            self.meta_receiver.new_jds.connect(self.on_new_jds) 
            self.meta_receiver.new_odr.connect(self.on_new_odr)
            self.meta_receiver.new_dpa.connect(self.on_new_dpa)
            self.meta_receiver.new_dpa_locked.connect(self.on_new_dpa)
            
        self.deck1 = Hyperdeck_driver(self.hydeck1_IP, self.hydeck1_label, self.clip_duration)        
        self.deck2 = Hyperdeck_driver(self.hydeck2_IP, self.hydeck2_label, self.clip_duration)
        self.deck3 = Hyperdeck_driver(self.hydeck3_IP, self.hydeck3_label, self.clip_duration)

        self.deck1.setInterclipDelay(self.deck1_delay)
        self.deck2.setInterclipDelay(self.deck2_delay)
        self.deck3.setInterclipDelay(self.deck3_delay)

        self.deck1.deck_connected.connect(self.on_deck1_init)
        self.deck2.deck_connected.connect(self.on_deck2_init)
        self.deck3.deck_connected.connect(self.on_deck3_init)

        self.deck1.new_msg.connect(self.on_deck1_new_msg)
        self.deck2.new_msg.connect(self.on_deck2_new_msg)
        self.deck3.new_msg.connect(self.on_deck3_new_msg)

        self.deck1.new_log_msg.connect(self.on_deck1_new_log_msg)
        self.deck2.new_log_msg.connect(self.on_deck2_new_log_msg)
        self.deck3.new_log_msg.connect(self.on_deck3_new_log_msg)

        self.deck1.new_status.connect(self.on_deck1_new_status)
        self.deck2.new_status.connect(self.on_deck2_new_status)
        self.deck3.new_status.connect(self.on_deck3_new_status)

        self.deck1.new_slot_info.connect(self.on_deck1_new_slot_info)
        self.deck2.new_slot_info.connect(self.on_deck2_new_slot_info)
        self.deck3.new_slot_info.connect(self.on_deck3_new_slot_info)

        self.deck1.clip_closed.connect(self.on_deck1_clip_closed)
        self.deck1.new_clip.connect(self.on_new_deck1_clip)
        self.deck2.clip_closed.connect(self.on_deck2_clip_closed)
        self.deck2.new_clip.connect(self.on_new_deck2_clip)
        self.deck3.clip_closed.connect(self.on_deck3_clip_closed)
        self.deck3.new_clip.connect(self.on_new_deck3_clip)

    def on_new_meta(self, srt1, srt2, srt3, srt4):
        self.ui.srtGB_pte.appendPlainText("New subtitles and metadata log")
        self.ui.srtGB_pte.appendPlainText(srt1)
        self.ui.srtGB_pte.appendPlainText(srt2)
        self.ui.srtGB_pte.appendPlainText(srt3)
        self.ui.srtGB_pte.appendPlainText(srt4)
        self.ui.srtGB.setStyleSheet("QGroupBox#srtGB {background: darkRed}")

    def on_meta_closed(self, timestr):
        return
        self.ui.srtGB_pte.appendPlainText("Subtitles and metadata log closed at " + timestr)
        self.ui.srtGB.setStyleSheet("QGroupBox#srtGB {background: green}")
        
    def on_deck1_new_status(self, ts, tid):
        # ts = transport status
        # tid = transport info dictionasry
        self.ui.deck1_status_pte.appendPlainText(ts + " mode" )
        self.ui.deck1_status_pte.appendPlainText("active slot " + tid['slot id'])
        
    def on_deck2_new_status(self, ts, tid):
        self.ui.deck2_status_pte.appendPlainText(ts + " mode" )
        self.ui.deck2_status_pte.appendPlainText("active slot " + tid['slot id'])

    def on_deck3_new_status(self, ts, tid):
        self.ui.deck3_status_pte.appendPlainText(ts + " mode" )
        self.ui.deck3_status_pte.appendPlainText("active slot " + tid['slot id'])

    def on_deck1_new_slot_info(self, s1d, s2d):
        # s1d = slot 1 status
        # tid = slot 2 status
        self.ui.deck1_status_pte.appendPlainText("SD1: " + s1d['status'])
        s1_timeleft = secs2ms(s1d['recording time'])
        self.ui.deck1_status_pte.appendPlainText("SD1 full in " + s1_timeleft)
        self.ui.deck1_status_pte.appendPlainText("SD2: " + s2d['status'])
        s2_timeleft = secs2ms(s2d['recording time'])
        self.ui.deck1_status_pte.appendPlainText("SD2 full in " + s2_timeleft)

    def on_deck2_new_slot_info(self, s1d, s2d):
        # s1d = slot 1 status
        # tid = slot 2 status
        self.ui.deck2_status_pte.appendPlainText("SD1: " + s1d['status'])
        s1_timeleft = secs2ms(s1d['recording time'])
        self.ui.deck2_status_pte.appendPlainText("SD1 full in " + s1_timeleft)
        self.ui.deck2_status_pte.appendPlainText("SD2: " + s2d['status'])
        s2_timeleft = secs2ms(s2d['recording time'])
        self.ui.deck2_status_pte.appendPlainText("SD2 full in " + s2_timeleft)

    def on_deck3_new_slot_info(self, s1d, s2d):
        # s1d = slot 1 status
        # tid = slot 2 status
        self.ui.deck3_status_pte.appendPlainText("SD1: " + s1d['status'])
        s1_timeleft = secs2ms(s1d['recording time'])
        self.ui.deck3_status_pte.appendPlainText("SD1 full in " + s1_timeleft)
        self.ui.deck3_status_pte.appendPlainText("SD2: " + s2d['status'])
        s2_timeleft = secs2ms(s2d['recording time'])
        self.ui.deck3_status_pte.appendPlainText("SD2 full in " + s2_timeleft)

    def on_deck1_new_msg(self, msg):
        self.ui.clipGB_pte.appendPlainText(systime() + " MSG: " + msg + "\n" )

    def on_deck2_new_msg(self, msg):
        self.ui.clipGB_2pte.appendPlainText(systime() + " MSG: " + msg + "\n" )

    def on_deck3_new_msg(self, msg):
        self.ui.clipGB_3pte.appendPlainText(systime() + " MSG: " + msg + "\n" )

    def on_deck1_new_log_msg(self, msg):
        logging.debug(msg)

    def on_deck2_new_log_msg(self, msg):
        logging.debug(msg)
        
    def on_deck3_new_log_msg(self, msg):
        logging.debug(msg)
        
    def on_deck1_clip_closed(self, cn):
        if self.subtitleGen.isInitiated() == True:
            logging.debug("Stop writing subtitles")
            self.subtitleGen.stop_logging()
            self.ui.srtGB_pte.appendPlainText("Subtitles stopped")
            
        self.ui.clipGB_pte.appendPlainText(cn + " closed at " + systime() )
        
        if self.clip_duration != 0:
            self.clipTimeRemaining = self.clip_minutes * 60
        else:
            self.clipTimeRemaining = -999.99
        
    def on_new_deck1_clip(self, cn):
        self.subtitleGen.start_logging()
        self.ui.clipGB_pte.appendPlainText("New clip started " + cn )
        self.deck1.setInterclipDelay(self.deck1_delay)
        self.deck2.setInterclipDelay(self.deck2_delay)
        self.deck3.setInterclipDelay(self.deck3_delay)
        self.get_decks_delays()
        
    def on_deck2_clip_closed(self, cn):
        self.ui.clipGB_2pte.appendPlainText(cn + " closed at " + systime() )

    def on_new_deck2_clip(self, cn):
        self.ui.clipGB_2pte.appendPlainText("New clip started " + cn )

    def on_deck3_clip_closed(self, cn):
        self.ui.clipGB_3pte.appendPlainText(cn + " closed at " + systime() )

    def on_new_deck3_clip(self, cn):
        self.ui.clipGB_3pte.appendPlainText("New clip started " + cn )

    def at_disp_systime_timeout(self):
        self.now = systime()
        self.now_f = systimef_s();
        self.ui.DateTimeDisp.setText(self.now_f)

    def on_new_lowID(self, newlowID):
        if newlowID != self.lowID:
            self.lowID = newlowID
            self.ui.LowIDlabel.setText(self.lowID.rstrip('\n'))

    def on_new_dpa(self, new_dpa):
        self.subtitleGen.updateDPAmsg(new_dpa)
        self.ui.DPAflash.setStyleSheet("QLabel {background: green}")
        self.dpaflashtimer.start(self.flash_on_duration)

    def on_new_dpa_locked(self, new_dpal, flag):
        self.subtitleGen.updateDPAlck(new_dpa, flag)

    def get_decks_delays(self):
        # passed to instance of hyperdeck.py by child method
        # setInterclipDelay. It expects the dely value to be in seconds.
        self.deck1_delay, self.deck2_delay, self.deck3_delay = \
            random.sample([1.96, 1.98, 2.0, 2.02, 2.04],k=3)
        
    def on_new_jds(self, new_jds):
        self.subtitleGen.updateJDS(new_jds)
        self.ui.JDSflash.setStyleSheet("QLabel {background: green}")
        self.jdsflashtimer.start(self.flash_on_duration)

    def on_new_odr(self, new_odr):
        self.odr_has_been_received = True
        self.ui.startButton.setEnabled(True)
        self.subtitleGen.updateODR(new_odr)
        self.ui.ODRflash.setStyleSheet("QLabel {background: green}")
        self.odrflashtimer.start(self.flash_on_duration)

    def on_dpaflashtimer_timeout(self):
        self.ui.DPAflash.setStyleSheet("QLabel {background: white}")
    
    def on_jdsflashtimer_timeout(self):
        self.ui.JDSflash.setStyleSheet("QLabel {background: white}")

    def on_odrflashtimer_timeout(self):
        self.ui.ODRflash.setStyleSheet("QLabel {background: white}")

    def on_deck1_init(self, cam):
        self.ui.clipGB.setStyleSheet("QGroupBox#Deck1GB {background: green}")

    def on_deck2_init(self, cam):
        self.ui.clipGB_2.setStyleSheet("QGroupBox#Deck2GB {background: green}")

    def on_deck3_init(self, cam):
        self.ui.clipGB_3.setStyleSheet("QGroupBox#Deck3GB {background: green}")

    def at_cliptimerheartbeat_timeout(self):
        self.clipTimeRemaining -= 1
        ctr = secs2ms(self.clipTimeRemaining)
        self.ui.clipTimeLabel.setText(ctr)
        
    def do_init(self, inifname):

        self.lowID=""

        ip = configparser.ConfigParser()
        ip.read(inifname)

        self.hydeck1_IP=ip.get('NETWORK','hydeck1_IP')
        self.hydeck2_IP=ip.get('NETWORK','hydeck2_IP')
        self.hydeck3_IP=ip.get('NETWORK','hydeck3_IP')
        self.ListenPort=int(ip.get('NETWORK','ListenPort'))

        self.hydeck1_label=ip.get('DECK','hydeck1_label')
        self.hydeck2_label=ip.get('DECK','hydeck2_label')
        self.hydeck3_label=ip.get('DECK','hydeck3_label')

        self.clip_minutes = int(ip.get('CLIP','clip_duration_minutes'))
        self.clip_duration = self.clip_minutes * 60 * 1000
        self.clipTimeRemaining=(self.clip_minutes * 60)
        
        self.ID2GB = {
            'clipGB':self.hydeck1_label,
            'clipGB_2':self.hydeck2_label,
            'clipGB_3':self.hydeck3_label,
            }

        for key in self.ID2GB.keys():
            do = ( "self.ui."+key+".setTitle('"+self.ID2GB[key]+"')" )
            eval(do)

        self.odr_has_been_received = False            

        self.ui.clipGB.setObjectName("Deck1GB")
        self.ui.clipGB_2.setObjectName("Deck2GB")
        self.ui.clipGB_3.setObjectName("Deck3GB")
        self.ui.srtGB.setObjectName("srtGB")
        
        # Set up timers that define flash of a UI box upon receipt of
        # JDS and ODR packets. The flash is intiated by a signal from
        # UDPreceiver, the timer shuts down the flash.
        self.flash_on_duration = 200  # milliseconds
        self.odrflashtimer=QTimer()
        self.odrflashtimer.timeout.connect(self.on_odrflashtimer_timeout)
        self.jdsflashtimer=QTimer()
        self.jdsflashtimer.timeout.connect(self.on_jdsflashtimer_timeout)
        self.dpaflashtimer=QTimer()
        self.dpaflashtimer.timeout.connect(self.on_dpaflashtimer_timeout)
        
        self.disp_systime_timer = QTimer()
        self.disp_systime_timer.timeout.connect(self.at_disp_systime_timeout)
        self.disp_systime_timer.start(1000)        

        self.clipTimeHeartbeatTimer = QTimer()
        self.clipTimeHeartbeatTimer.timeout.connect(self.at_cliptimerheartbeat_timeout)

        self.get_decks_delays()

    def on_start_button(self):

        if ( self.deck1.isInitiated() == False):
            self.deck1.manual_start()
            self.ui.clipGB.setStyleSheet("QGroupBox#Deck1GB { background: darkRed}")
        if ( self.deck2.isInitiated() == False):
            self.deck2.manual_start()
            self.ui.clipGB_2.setStyleSheet("QGroupBox#Deck2GB {background: darkRed}")
        if ( self.deck3.isInitiated() == False):
            self.deck3.manual_start()
            self.ui.clipGB_3.setStyleSheet("QGroupBox#Deck3GB {background: darkRed}")

        self.ui.recIconLabel.setStyleSheet("QLabel {background: darkRed}")

        self.cliptimecounter = 0
        self.clipTimeHeartbeatTimer.start(1000)
        
    def on_stop_button(self):

        if ( self.deck1.isInitiated() == True):
            self.deck1.manual_stop()
            self.ui.clipGB.setStyleSheet("QGroupBox#Deck1GB {background: green}")

        if ( self.deck2.isInitiated() == True):
            self.deck2.manual_stop()
            self.ui.clipGB_2.setStyleSheet("QGroupBox#Deck2GB {background: green}")

        if ( self.deck3.isInitiated() == True):
            self.deck3.manual_stop()
            self.ui.clipGB_3.setStyleSheet("QGroupBox#Deck3GB {background: green}")

        if ( self.subtitleGen.isInitiated() == True):
            self.subtitleGen.stop_logging()
            self.ui.srtGB.setStyleSheet("QGroupBox#srtGB {background: green}")

        self.ui.recIconLabel.setStyleSheet("QLabel {background: gray}")
        self.cliptimecounter = 0
        self.clipTimeHeartbeatTimer.stop()

    def on_estop_button(self):
        # For use when hyper-rec.py has crshed but the hdecks still record
        
        self.deck1.manual_stop()
        self.ui.clipGB.setStyleSheet("QGroupBox#Deck1GB {background: gray}")

        self.deck2.manual_stop()
        self.ui.clipGB_2.setStyleSheet("QGroupBox#Deck2GB {background: gray}")

        self.deck3.manual_stop()
        self.ui.clipGB_3.setStyleSheet("QGroupBox#Deck3GB {background: gray}")

    def on_quit_button(self):
        self.ui.quitButton.setText("Quitting")
        self.ui.quitButton.setStyleSheet("QPushButton {background: green}")

        if self.subtitleGen.isInitiated() == True:
            self.subtitleGen.stop_logging()
        
        self.deck1.set_clipping(False)
        self.deck2.set_clipping(False)
        self.deck1.set_clipping(False)
        
        self.deck1.manual_stop()
        self.deck2.manual_stop()
        self.deck3.manual_stop()

#        self.deck1.manual_quit()
#        self.deck2.manual_quit()
#        self.deck3.manual_quit()

        QCoreApplication.exit()

if __name__ == "__main__":

    # Minor config here. User defines config filename.
    ini_filename = "hyper_rec.ini"

    app = QApplication(sys.argv)

    ini_filename="hyper_rec.ini"
    hr=HyperRecGUI(ini_filename)
    hr.show()
        
    sys.exit(app.exec_())
