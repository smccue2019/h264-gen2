#!/usr/bin/env python3
from PyQt5.QtCore import QThread,pyqtSignal, QTimer, QDateTime, QEventLoop
import string, socket, re
import logging, asyncio
from sjm_pkg.responseParser import responseParser

class Hyperdeck_driver(QThread):

    new_clip = pyqtSignal(str, name = 'new_clip')
    clip_closed = pyqtSignal(str, name = 'clip_closed')
    deck_connected = pyqtSignal(str, name = 'deck_connected')

    def __init__(self,deck_ip,camera_name,clip_duration):
        QThread.__init__(self, parent=None)
        self.deck_ip = deck_ip
        self.deck_port = 9993
        self.camera_name = camera_name

        myloggername = ("decks_" + systimeNozz() + ".log")
        logging.basicConfig(filename=myloggername, level=logging.DEBUG)

        self.initiated = False
        self.busy = False
        self.Recording = False
        self.ok2go = False
        self.response = ""

        self.ok2go, response=self.cmd_to_deck('configuration')

        if response:
            logging.info(systimef() + " " + self.camera_name + " " + response) 
        else:
            print(self.camera_name + " deck did not respond to initial query")
            
        # It appears that duration should be desired minus roughly 1 second.
        # QTimer wants milliseconds
        # Calculated from clip_duration so that deck close and open
        # delay can be accounted. Early tests suggest one second works.

        self.close2open_delay = 2.0
        self.duration4deck=( 1000 *( ((clip_duration - 1)*60) + (60 - self.close2open_delay) ) )

        self.clip_timer = QTimer()
        self.clip_timer.timeout.connect(self.at_clip_timeout)

        self.status_update_interval_secs = 10;
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_status)
        
    def manual_start(self):
        if self.initiated == False:        
            self.initiated = True
            self.status_update_timer.start(self.status_update_interval_secs * 1000)
            self.start_new_clip()

    def manual_stop(self):
        if self.isInitiated() == True:
            self.initiated = False
            self.stop_clip()
            
    def start_new_clip(self):
        self.gen_outfilename()  # generates self.clipname
        record_cmd = ('record: name:' + self.camoutfile)
        self.ok2go, response=self.cmd_to_deck(record_cmd)
        if response:
            logging.info(systimef() + " " + record_cmd + "\n"  + response)
        elif self.ok2go and not response:
            print("Got an OK but no response from record cmd")
        else:
            print(self.camera_name + " deck did not respond to record command")
        self.clip_timer.start(self.duration4deck)
        self.new_clip.emit(self.camoutfile)

    def restart_clip(self):
        self.gen_outfilename()  # generates self.clipname
        record_cmd = ('record: name:' + self.camoutfile)
        self.ok2go, response=self.cmd_to_deck(record_cmd)
        if response:
            logging.info(systimef() + " " + record_cmd + "\n"  + str(response))
        elif self.ok2go and not response:
            print("Got an OK but no response from record cmd")
        else:
            print(self.camera_name + " deck did not respond to record command")
       
    def stop_clip(self):
        self.ok2go, response = self.cmd_to_deck('stop')
        if response:
            logging.info(systimef() + "STOP\n"  + response)
        elif self.ok2go and not response:
            print("Got an OK but no response from stop cmd")
        else:
            print(self.camera_name + " deck did not respond to stop command")

        self.clip_timer.stop()
        logging.info(systimef() + " stop " + self.camera_name + " " + response) 
        self.clip_closed.emit(systime())


        if ( self.ok2go  and self.isInitiated() == True ):
            QTimer.singleShot((1000.0 * self.close2open_delay),self.start_new_clip)  
            #self.start_new_clip()

    def cmd_to_deck(self, cmd):
        if self.busy == False:
            self.busy = True

            if (cmd == 'transport info'):
                print("Transport info status requested")
                raw_response = self.mynetcat(cmd)
                if (raw_response):
                    rp = responseParser(raw_response)
                    self.busy = False
                    if self.isInitiated():
                      if rp.getRecordingState() == True:
                          print("Recording requested and ON")
                          return(True, "Recording requested and ON")
                      else:
                          print("ERROR: Recording requested and OFF")
                          return(False, "ERROR: Recording requested and OFF")
                    else:
                      if rp.getRecordingState() == True:
                          print("ERROR: Recording NOT initiated and ON")
                          return(False, "ERROR: Recording NOT initiated and ON")
                      else:
                          print("Recording not initiated and OFF")
                          return(False, "Recording not initiated and OFF")
                        
            else:
                raw_response = self.mynetcat(cmd)
                self.busy = False
                rp=responseParser(raw_response)
                ok_or_not = rp.isOK2proceed()
                if ok_or_not:
                    r=rp.getResponse()
                    print(r)
                    return (ok_or_not, r)
                else:
                    e = rp.getErrorCode()
                    return (ok_or_not, e)
        
    def mynetcat(self, content):
        newline=0x0A
        fulldata=bytearray()
        
        mycontent=bytearray( content, 'utf-8' )
        mycontent.append(newline)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.deck_ip, self.deck_port))
        s.sendall(mycontent)
        mysleep(500)
        s.shutdown(socket.SHUT_WR)
        
        while True:
            data = s.recv(4096)
            if data: 
                fulldata.extend(data)
            else:
                break
        s.close()
        return(fulldata.decode('utf-8'))
    
    def isInitiated(self):
        return self.initiated

    def at_clip_timeout(self):
        self.stop_clip()

    def gen_outfilename(self):
        self.camoutfile = "%s_%s" % (self.camera_name, systime())

    def get_camoutfile(self):
        return self.camoutfile

    def update_status(self):
        # The transport info command is made a special case
        # by the hyperdeck interface.
        command = 'transport info'
        good_or_not = False
        (good_or_not, info_str) = self.cmd_to_deck(command)

        if info_str:
            logging.info(systimef() + "transport info\n"  + info_str)
        else:
            print(self.camera_name + " deck did not respond to transport info command")
        if ( (not good_or_not) and self.isInitiated() ):
            self.restart_clip()
        
def systime():
    now = QDateTime.currentDateTime()
    systime = now.toString("yyyyMMddhhmmss.zz")
    return systime

def systimeNozz():
    now = QDateTime.currentDateTime()
    systime = now.toString("yyyyMMddhhmmss")
    return systime

def systimef():
    now = QDateTime.currentDateTime()
    systimef = now.toString("yyyy/MM/dd hh:mm:ss.zz")
    return systimef

def mysleep(sleeptime):
    loop = QEventLoop()
    QTimer.singleShot(sleeptime, loop.quit )
    loop.exec_()
