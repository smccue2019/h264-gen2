#!/usr/bin/env python3
import string
from PyQt5.QtCore import QObject, pyqtSignal

class responseParser(QObject):

    rp_status = pyqtSignal(bool, name = 'rp_status')
    
    def __init__(self, raw_response):

        super(responseParser, self).__init__()

        self.rp_status.emit(True)
        self.response = ()
        self.ok2proceed = False
        self.error_code = 0
        self.raw_response = raw_response
        self.classify()

        #print(raw_response)
        
    def classify(self):
        self.isRecording = False
        self.isIdle = False
        
        if len(self.raw_response) == 0:
            print("Raw response length is zero")
            self.ok2proceed = False
            self.rp_status.emit(False)
            return

        response_lines = self.raw_response.split('\n')

        # Every response includes four lines of a type '500' stanza.
        # Remove these and handle the stanza that follows.
        self.firstline = response_lines[4]
        self.response_code = int(self.firstline.split(' ', 1)[0])
        self.l1_comment1 = self.firstline.split(' ', 1)[1]
        self.l1_fullcomment = ' '.join(self.firstline.split(' ', 1)[1:])
        self.cleaned_response = response_lines[4:]
        
        try:
            secondline = response_lines[5]
            if self.response_code == 208:
                status = secondline.split()[1]
                if status == 'record':
                    self.isRecording = True
                else:
                    self.isRecording = False
            elif self.response_code == 200:
                if self.l1_comment1 == 'ok':
                    self.ok2proceed = True
            elif self.response_code == 104:
                self.ok2proceed = False
                self.error_code = "SD-card-full"
            elif self.response_code == 105:
                self.ok2proceed = False
                self.error_code = "SD-card-missing"
            elif self.response_code == 500:
                print("Connect response 500")
                self.ok2proceed = False
            elif ( (self.response_code > 200) and (self.response_code < 300) ):
                # Basically, "OK will do"
                self.ok2proceed = True
                print("GOOD: Connect response is " + self.response_code)
            elif ( (self.response_code >= 100) and (self.response_code < 200) ):
                self.ok2proceed = False
                self.error_code = self.response_code
                print("PROBLEM: Connect response is " + self.response_code)

        except:
            throwaway = "Didn't find or couldn't parse second line"
            
        self.rp_status.emit(False)
    def isOK2proceed(self):
        return self.ok2proceed
    
    def getErrorCode(self):
        return self.error_code

    def getResponse(self):
        r = str(self.cleaned_response[0] + "\n" + self.cleaned_response[1])
        if r == None:
            r = "Missing response"
        else:
            # r = str(self.cleaned_response[0] + "\n" + self.cleaned_response[1])
            r = self.firstline

        return r
    
    def getRecordingState(self):
        return self.isRecording

#    def getIdleState(self):
#        return self.isIdle
