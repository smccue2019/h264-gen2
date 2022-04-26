#!/usr/bin/env python3
import sys, re, time, threading
from math import isnan
from PyQt5.QtCore import Qt, QTime, QTimer, pyqtSignal, QFile
from PyQt5 import QtNetwork
from PyQt5.QtWidgets import QDialog

class UDPreceiver(QDialog):

# SJM Sept 2015
#    new_altitude = pyqtSignal(float, float, name = 'new_altitude')
    new_altitude = pyqtSignal(float, name = 'new_altitude')
    new_jds = pyqtSignal(str, name = 'new_jds')
    new_odr = pyqtSignal(str, name = 'new_odr')
    new_csv = pyqtSignal(str, name = 'new_csv')
    new_dpa = pyqtSignal(str, name = 'new_dpa')
    new_dpa_locked = pyqtSignal(float, int, name = 'new_dpa_locked')

    def __init__(self, listen_port, parent=None):
        super(UDPreceiver, self).__init__(parent)

        self.ListenPort = listen_port

        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(QtNetwork.QHostAddress.Any, self.ListenPort)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)

    def processPendingDatagrams(self):
        while self.udpSocket.hasPendingDatagrams():
            udpbytearr, host, port = \
               self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
            udpstr = udpbytearr.decode('utf-8')

            u = datagram2packetID(udpstr)
            id_string = u.identify_datagram()
            if id_string == 'JDS':
                self.parseJDS(udpstr)
            elif id_string == 'ODR':
                self.new_odr.emit(udpstr)
            elif id_string == 'CSV':
                self.new_csv.emit(udpstr)
            elif id_string == 'DPA':
                self.new_dpa.emit(udpstr)
                (dvl_alt, flag) = self.parseDPA(udpstr)
            else:
                # Other packets don't matter
                pass

    def parseDPA(self,dpapkt):
        dpapkt.rstrip('\n')
        dpa_fields = dpapkt.split(" ")
        try:
            dop_alt = float(dpa_fields[4])
        except ValueError:
            dop_alt = nan
        try:
            bottom_lock_status = int(dpa_fields[5])
        except ValueError:
            lock_status = nan
            
        self.new_dpa_locked.emit(dop_alt, bottom_lock_status)
        return (dop_alt, bottom_lock_status)

    def parseJDS(self, jdspkt):
# "JDS 2012/04/13 16:52:39 JAS2 11.6877602 -58.5421899 851.68 6020.31 0.0 -3.2 244.02 1327.99 0.81 24356.0 -0.5."

#        print(jdspkt)
        jdspkt.rstrip('\n')
        jdsfields  = jdspkt.split(" ")
        pktid = jdsfields[0]
        jdsdate = jdsfields[1]
        jdstime = jdsfields[2]
        veh = jdsfields[3]
        latitude_deg = float(jdsfields[4])
        longitude_deg = float(jdsfields[5])
        X_local = float(jdsfields[6])
        Y_local = float(jdsfields[7])
        octans_roll = float(jdsfields[8])
        octans_pitch = float(jdsfields[9])
        octans_heading = float(jdsfields[10])
        depth = float(jdsfields[11])
        unk1 = jdsfields[13]
        unk2= jdsfields[14]

        # Altitude can be wrong for several reasons. one
        # of them is that the vehicle is too high in the
        # water column. If it's not reporting a number,
        # then set it to something that's definitely
        # not-a-number.
        try:
            altitude = float(jdsfields[12])
        except ValueError:
            altitude = nan

        self.new_altitude.emit(altitude)
        self.new_jds.emit(jdspkt)

        return altitude

class datagram2packetID():

    def __init__(self, datagram):

        self.datagram = datagram
        self.o = re.compile('^ODR')
        self.j = re.compile('^JDS')
        self.c = re.compile('^CSV')
        self.d = re.compile('^DPA')

    def identify_datagram(self):

        if self.o.match(self.datagram):
            return('ODR')
        elif self.j.match(self.datagram):
            return('JDS')
        elif self.c.match(self.datagram):
            return('CSV')
        elif self.d.match(self.datagram):
            return('DPA')
        else:
            #print("Unidentified datagram")
            return None
