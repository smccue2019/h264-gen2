#!/usr/bin/env python3
from PyQt5.QtCore import QThread,pyqtSignal, QTimer
from PyQt5.QtTest import QTest
import string, socket, re
import logging
from time import sleep
from sjm_pkg.responseParser import responseParser
from sjm_pkg.time_routines import systime, systimef, systime_s
import json

class Hyperdeck_driver(QThread):

    deck_connected = pyqtSignal(bool, name = 'deck_connected')
    new_clip = pyqtSignal(str, str, name = 'new_clip')
    clip_closed = pyqtSignal(str, str, name = 'clip_closed')
    new_msg = pyqtSignal(str, name = 'new_msg')
    new_status = pyqtSignal(str, dict, name = 'new_status')
    new_slot_info = pyqtSignal(dict, dict, name = 'new_slot_info')
    error_code = pyqtSignal(str, str, name = 'error_code')
    
    def __init__(self,deck_ip,camera_name,clip_duration):
        QThread.__init__(self, parent=None)
        self.deck_ip = deck_ip
        self.deck_port = 9993
        self.cn = camera_name
        self.camoutfile=""
        self.clip_duration = clip_duration

        myloggername = (self.cn + "_" + systime_s() + ".log")
        print(myloggername)
        logging.basicConfig(filename=myloggername, level=logging.DEBUG)

        self.initiated = False
        self.Recording = False
        self.response = ""
        
        self.start()
        
    def start(self):
        self.do_init()
        logstr = ("Logging of " + self.cn + " started " + systime_s())
        logging.info(logstr)

        response = self.cmd_to_deck('ping')
        if not response['error']:
            self.deck_connected.emit(True)
        else:
            self.new_msg.emit("Error connecting")
            logging.info(systimef() + " " + self.cn + " " + str(response['code']))
            
        if (self.clip_duration == 0):
            self.set_clipping(False)
        else:
            self.set_clipping(True)
            
            self.clip_timer = QTimer()
            self.clip_timer.timeout.connect(self.at_clip_timeout)

        self.status_update_interval_secs = 5;
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_status)
        self.status_update_timer.start(self.status_update_interval_secs * 1000)
        
    def manual_start(self):
        self.initiated = True
        self.start_new_clip()

    def manual_stop(self):
        self.initiated = False
        self.stop_clip()

    def manual_quit(self):
        self.cmd_to_deck('quit')
        
    def start_new_clip(self):
        if self.initiated:
            self.gen_outfilename()
            record_cmd = ('record: name:' + self.camoutfile)
            response=self.cmd_to_deck(record_cmd)
            logstr = (systimef() + ":" + self.cn + " New clip\n")
            logging.info(logstr)

            if self.do_clipping:
                self.clip_timer.start(self.clip_duration)
                self.new_clip.emit(self.camoutfile, systime())

            return logstr
        else:
            return

    def set_clipping(self, new_setting):
        # Boolean
        self.do_clipping = new_setting

    def get_clipping(self):
        return self.do_clipping
        
    def stop_clip(self):

        response = self.cmd_to_deck('stop')
        logstr = (systimef() + ":" + self.cn + " Stop recording\n")
        logging.info(logstr)
        self.clip_closed.emit(self.camoutfile, systime())
            
        if self.do_clipping:
            self.clip_timer.stop()
            #QTest.qWait(2000)
            QTimer.singleShot(2000, self.start_new_clip)
            #self.start_new_clip()
        return logstr

    def cmd_to_deck(self, cmd):    
        raw_response = self.mynetcat(cmd)
        response = self.parse_response(raw_response)
        return response
        
    def mynetcat(self, content):
        newline=0x0A
        fulldata=bytearray()
        
        mycontent=bytearray( content, 'utf-8' )
        mycontent.append(newline)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.deck_ip, self.deck_port))
        s.sendall(mycontent)
        QTest.qWait(200)
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
        self.camoutfile = "%s_%s" % (self.cn, systime())

    def get_camoutfile(self):
        return self.camoutfile

    def parse_response(self, the_response):

        the_response_lines = list(the_response.split('\r\n'))
        # Every response includes four lines of a type '500' stanza.
        # Remove these and handle the stanza that follows.
        myresponse_lines = the_response_lines[4:]
        #print(myresponse_lines)
        
        response_code = int(myresponse_lines[0].split(' ', 1)[0])
        #print(response_code)
        
        is_error_response = response_code >= 100 and response_code < 200
        is_async_response = response_code >= 500 and response_code < 600

        response = {
            'error': is_error_response,
            'code': response_code,
            'lines': myresponse_lines,
        }

        if is_error_response:
            self.error_code.emit(response['code'], self.error_code_map[response['code']])
        return response

    def update_status(self):
        # Obtain statuses of transport and SD media (slot info)
        
        transport_response = self.cmd_to_deck('transport info')

        if transport_response['code'] == 208:
            # get transport status from first line, also make a dict of full status report
            (name, value) = transport_response['lines'][1].split(': ')
            transport_status = value
            
            self.detailed_transport_stat = dict()
           
            # Each line past the first response line contains an individual
            # property of the HyperDeck, such as the play state.
            transport_info = transport_response['lines'][1:]
            for line in transport_info:

                result = line.split(': ')
                if len(result) == 2:
                    [name, value] = (result[0],result[1])
                    self.detailed_transport_stat[name] = value

        self.new_status.emit(transport_status, self.detailed_transport_stat)

        ################# Slots Queries #################
        self.detailed_slot1_dict = {}
        self.detailed_slot2_dict = {}
#Slot 1        
        slot_query_cmd = ("slot info: slot id: 1")
        slot_response = self.cmd_to_deck(slot_query_cmd)
        #print(slot_response['code'])
        #print(slot_response['lines'])
        (name, slotnum) = slot_response['lines'][1].split(': ')
        if slot_response['code'] == 202 and int(slotnum) == 1:
            # Each line past the first response line contains a
            # property of the slot 1.
            slot_info = slot_response['lines'][1:]
            for line in slot_info:
                result = line.split(': ')
                if len(result) == 2:
                    [name, value] = (result[0],result[1])
                    self.detailed_slot1_dict[name] = value
        # Slot 2
        slot_query_cmd = ("slot info: slot id: 2")
        slot_response = self.cmd_to_deck(slot_query_cmd)
        #print(slot_response['code'])
        #print(slot_response['lines'])
        (name, slotnum) = slot_response['lines'][1].split(': ')
        if slot_response['code'] == 202 and int(slotnum) == 2:
            # Each line past the first response line contains a
            # property of the slot 2.
            slot_info = slot_response['lines'][1:]
            for line in slot_info:
                result = line.split(': ')
                if len(result) == 2:
                    [name, value] = (result[0],result[1])
                    self.detailed_slot2_dict[name] = value

        self.new_slot_info.emit(self.detailed_slot1_dict, self.detailed_slot2_dict)

    def do_init(self):

        self.error_code_map = {
            '100': 'syntax-error',
            '104': 'SD-card-full',
            '105': 'SD-card-missing',
            '106': 'SD-card-error',
            '110': 'no-input',
            '111': 'remote-control-disabled',
        }

        self.good_code_map = {
            '200': 'OK',
            '202': 'slot-response',
            '208': 'status-response',
        }
        
