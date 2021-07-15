#!/usr/bin/env python3
import string
from PyQt5.QtCore import QObject

class responseParser(QObject):

    def __init__(self, raw_response):
        super(responseParser, self).__init__()

        self.response = ()
        self.ok2proceed = False
        self.error_code = 0
        self.raw_response = raw_response
        self.classify()

        print(raw_response)
        
    def classify(self):
        self.isRecording = False
        self.isIdle = False
        
        if len(self.raw_response) == 0:
            print("Raw response length is zero")
            self.ok2proceed = False
            return

        response_lines = self.raw_response.split('\n')

        # Every response includes four lines of a type '500' stanza. Remove these and
        # handle the stanza that follows.
        self.firstline = response_lines[4]
        self.response_code = int(self.firstline.split(' ', 1)[0])
        self.response_comment1 = self.firstline.split(' ', 1)[1]

        try:
            secondline = response_lines[5]
            if self.response_code == 208:
                status = secondline.split()[1]
                if status == 'record':
                    self.isRecording = True
                elif status == 'idle':
                    self.isIdle = True
            elif self.response_code == 200:
                if self.response_comment1 == 'ok':
                    self.ok2proceed = True
        except:
            print("Didn't find or couldn't parse second line")
        
        self.cleaned_response = response_lines[4:]
        #print(self.cleaned_response)
        if self.response_code == 500:
            print("Connect response 500")
            self.ok2proceed = False
        elif ( (self.response_code >= 200) and (self.response_code < 300) ):
            # Basically, "OK will do"
            self.ok2proceed = True
        elif ( (self.response_code >= 100) and (self.response_code < 200) ):
            self.ok2proceed = False
            self.error_code = self.response_code
        
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

    def getIdleState(self):
        return self.isIdle
