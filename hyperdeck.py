#!/usr/bin/env python3
from PyQt5.QtCore import QThread,pyqtSignal, QTimer, QDateTime, QEventLoop
import string, socket, re

class Hyperdeck_driver(QThread):

    # Alert through Qt signalling to other threads- that this thread
    # has closed and opened a clip file.
    new_clip = pyqtSignal(str, name = 'new_clip')
    clip_closed = pyqtSignal(str, name = 'clip_closed')
    deck_connected = pyqtSignal(str, name = 'deck_connected')

    def __init__(self,deck_ip,camera_name,clip_duration):
        QThread.__init__(self, parent=None)
        self.deck_ip = deck_ip
        self.deck_port = 9993
        self.camera_name = camera_name

        
        self.initiated = False
        self.busy = False

        self.ping_to_deck('ping')
        
        # It appears that duration should be desired minus 1 second.
        # QTimer wants seconds
        # Calculated from clip_duration so that deck close and open
        # delay can be accounted. Early tests suggest one second works.

        self.close2open_delay = 1.5
        self.duration4deck=( 1000 *( ((clip_duration - 1)*60) + (60 - self.close2open_delay) ) )

        self.clip_timer = QTimer()
        self.clip_timer.timeout.connect(self.at_clip_timeout)
        
        
    def manual_start(self):
        if self.initiated == False:        
            self.initiated = True
            self.start_recording()

    def manual_stop(self):
        if self.isInitiated() == True:
            self.initiated = False
            self.stop_recording_part1()
            
    def start_recording(self):
        self.gen_outfilename()  # generates self.clipname
        print(self.camoutfile)
        
        record_cmd = ('record: name:' + self.camoutfile)
        print(record_cmd)
        self.cmd_to_deck(record_cmd)
        self.clip_timer.start(self.duration4deck)
        self.new_clip.emit(self.camoutfile)

    def stop_recording_part1(self):
        self.cmd_to_deck('stop')
        QTimer.singleShot(self.close2open_delay*1000, self.stop_recording_part2)

    def stop_recording_part2(self):
        print("Got to part2")
        self.clip_timer.stop()
        self.clip_closed.emit(systime())
        if self.isInitiated() == True:
            self.start_recording()
                
    def cmd_to_deck(self, cmd):
        if self.busy == False:
            self.busy = True
            self.response = self.mynetcat(cmd)
            self.busy = False

    def ping_to_deck(self, cmd):
        ping_regexp = re.compile('^500')
        
        ping_response = self.mynetcat('ping')
        #print(ping_response)
        if ping_regexp.match(ping_response):
            self.deck_connected.emit(ping_response)
            
    def mynetcat(self, content):
        newline=0x0A
        fulldata=bytearray()
        
        print("netcat message:" + content)
        mycontent=bytearray( content, 'utf-8' )
        mycontent.append(newline)
 #       print(mycontent)

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
        print("Clip timeout")
        self.stop_recording_part1()

    def gen_outfilename(self):
        self.camoutfile = "%s_%s.ts" % (self.camera_name, systime())

    def get_camoutfile(self):
        return self.camoutfile

def systime():
    now = QDateTime.currentDateTime()
    systime = now.toString("yyyyMMddhhmmss.zz")
    return systime
def systimef():
    now = QDateTime.currentDateTime()
    systimef = now.toString("yyyy/MM/dd hh:mm:ss.zz")
    return systimef

def mysleep(sleeptime):
    loop = QEventLoop()
    QTimer.singleShot(sleeptime, loop.quit )
    loop.exec_()
