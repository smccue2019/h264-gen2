#!/usr/bin/env python
import sys, string, pathlib, os
import re, datetime
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtCore import QTimer,QDateTime, QTextStream, QFile
from PyQt5.QtWidgets import QMessageBox
from sjm_pkg.time_routines import removeZZfromJDStime

class UDP2subtitle(QObject):

    meta_closed = pyqtSignal(str,name = 'meta_closed')
    new_meta = pyqtSignal(str,str,str,str,name = 'new_meta')
    lowID = pyqtSignal(str, name = 'lowID')

    def __init__(self):
        super(UDP2subtitle, self).__init__()        

        self.odr_received = False
        self.st_duration = 900.0    # millisecs, subtitle shown on
        self.odrdate = "01/01/1970"
        self.odrtime = "00:00:00"
        self.orglat  = 0.0
        self.orglon  = 0.0
        self.utm  =  0
        self.veh = "JAS2"
        self.cruiseid =  "Unknown"
        self.loweringid =  "Unknown"
        self.jdsdate = "01/01/1970"
        self.jdstime =  "00:00:00"
        self.latitude_deg =  0.0
        self.longitude_deg =  0.0
        self.X_local =  0.0
        self.Y_local =  0.0
        self.octans_roll =  0.0
        self.octans_pitch =  0.0
        self.octans_heading =  0
        self.depth =  0.0
        self.altitude =  0.0

        self.alt_str = "N/A" # Intro'ed by DPA record
        
        self.prior_cruiseid = "Unknown"
        self.prior_loweringid = "Unknown"

        self.update_metastrings()

        self.write2srtTimer = QTimer()
        self.write2srtTimer.timeout.connect(self.on_write2srt_timeout)

        self.initiated = False

    def start_logging(self):
        self.srt_counter=0
        self.gen_new_outnames()
        self.open_outfiles()
        self.start_msecs = epoch_msecs()
        self.write2srtTimer.start(1000)
        self.initiated = True

    def on_write2srt_timeout(self):
        self.out2log()
        self.out2srt()

    def out2log(self):
        self.logstream << systime() << "\n" 
        self.logstream << self.metastr1 << "\n"
        self.logstream << self.metastr2 << "\n"
        self.logstream << self.metastr3 << "\n"
        self.logstream << self.metastr4 << "\n"

    def out2srt(self):
        self.srt_counter += 1
        self.now_msecs = epoch_msecs()
        stanza_start_msec = self.now_msecs - self.start_msecs
        sstr = ms2srt_time_str(stanza_start_msec)
        stanza_end_msec = stanza_start_msec + self.st_duration
        estr = ms2srt_time_str(stanza_end_msec)

        self.srtstream1 << self.srt_counter << "\n"
        self.srtstream1 << sstr << "-->" << estr << "\n"
        self.srtstream1 << self.metastr1 << "\n"
        self.srtstream1 << "\n"

        self.srtstream2 << self.srt_counter << "\n"
        self.srtstream2 << sstr << "-->" << estr << "\n"
        self.srtstream2 << self.metastr2 << "\n"
        self.srtstream2 << "\n"

        self.srtstream3 << self.srt_counter << "\n"
        self.srtstream3 << sstr << "-->" << estr << "\n"
        self.srtstream3 << self.metastr3 << "\n"
        self.srtstream3 << "\n"

        # Commented out 4/28/22 because things run when commented,
        # seg fault when not. I dont yet know why.
#        self.srtstream4 << self.srt_counter << "\n"
#        self.srtstream4 << sstr << "-->" << estr << "\n"
#        self.srtstream4 << self.metastr4 << "\n"
#        self.srtstream4 << "\n"

    def updateDPAmsg(self, DPAmessage):
        # This one handles full record for logs
        # Bottom lock flag has no effect.
        # Might be superfluous, with updateDPAlck preferred
        #self.update_metastrings()
        pass
    
    def updateDPAlck(self, dvl_alt, lockflag):
        # This one reacts to bottom lock status
        if lockflag:
            # Can be used for autorecording
            self.alt_str = ("%4.1f") % (dvl_alt)
        else:
            self.alt_str = "N/A"

        self.update_metastrings()
        
    def updateODR(self, ODRmessage):
        (odate,otime,olat,olon,utmz,cruiseID,lowID) \
                                = self.parseODR(ODRmessage)

        # SJM 2/2021 Add outpath based on cruise ID and lowering ID

        if ( (self.cruiseid != self.prior_cruiseid) or \
             (self.loweringid != self.prior_loweringid) ):
            self.prior_cruiseid = cruiseID
            self.prior_loweringid = lowID
            self.odr_received = True

        self.odrdate = odate
        self.odrtime = otime
        self.orglat  = float(olat)
        self.orglon  = float(olon)
        self.utm  = int(utmz)
        self.cruiseid = cruiseID
        self.loweringid = lowID
        self.update_metastrings()
        self.lowID.emit(self.loweringid)
            
    def updateJDS(self, JDSmessage):
        (veh,datestr,timestr,lat_deg,lon_deg,X_local,Y_local,oct_roll, \
             oct_pitch,oct_heading,depth, altitude)=self.parseJDS(JDSmessage)
        self.veh = veh
        self.jdsdate = datestr
        self.jdstime = timestr
        self.latitude_deg = float(lat_deg)
        self.longitude_deg = float(lon_deg)
        self.X_local = float(X_local)
        self.Y_local = float(Y_local)
        self.octans_roll = float(oct_roll)
        self.octans_pitch = float(oct_pitch)
        self.octans_heading = int(oct_heading)
        self.depth = float(depth)
        self.altitude = altitude
        self.update_metastrings()
        
    def update_metastrings(self):
        st_jds=removeZZfromJDStime(self.jdstime)
        self.metastr1="%s %9.5f/%10.5f h=%d d=%d a=%s" % (st_jds, \
                                                      self.latitude_deg,\
                                                      self.longitude_deg,\
                                                      self.octans_heading,\
                                                      self.depth, self.alt_str)
        self.metastr2="veh=%s cr=%s lID=%s dt=%s"% (self.veh,self.cruiseid, \
                                       self.loweringid,self.jdsdate)
        self.metastr3="x=%10.3f y=%10.3f r=%8.3f p=%8.3f a=%8.3f" % (self.X_local, \
                                                           self.Y_local, \
                                                           self.octans_roll,\
                                                           self.octans_pitch, \
                                                           self.altitude)
        self.metastr4 = "orglt=%10.5f orgln=%10.5f utm=%d" % (self.orglat,self.orglon,self.utm)

    def new_clip(self):
        self.start_msec = epoch_msecs()
        self.srt_counter = 0
       
        self.close_outfiles()
        self.gen_new_outnames()
        self.open_outfiles()

    def close_outfiles(self):
        try:
            self.logfileh.close()
        except:
            print("failed to close logfile")

        try:
            self.srtfile1h.close()
        except:
            print("failed to close srtfile1")

        try:
            self.srtfile2h.close()
        except:
            print("failed to close srtfile2")

        try:
            self.srtfile3h.close()
        except:
            print("failed to close srtfile3")

        try:
            self.srtfile4h.close()
        except:
            print("failed to close srtfile4")

        self.meta_closed.emit( systime() )
        
    def open_outfiles(self):
        self.logfileh = QFile(self.logfile)
        self.srtfile1h = QFile(self.srtfile1)
        self.srtfile2h = QFile(self.srtfile2)
        self.srtfile3h = QFile(self.srtfile3)
        self.srtfile4h = QFile(self.srtfile4)

        if not self.logfileh.open(QFile.WriteOnly):
            QMessageBox.warning(self, \
                                self.tr \
                                ("Cant open file %1:\n%2").arg \
                                (self.logfile).arg(file.errorString()))

        if not self.srtfile1h.open(QFile.WriteOnly):
            QMessageBox.warning(self, \
                                self.tr \
                                ("Cant open file %1:\n%2").arg \
                                (self.srtfile1).arg(file.errorString()))

        if not self.srtfile2h.open(QFile.WriteOnly):
            QMessageBox.warning(self, \
                                self.tr \
                                ("Cant open file %1:\n%2").arg \
                                (self.srtfile2).arg(file.errorString()))

        if not self.srtfile3h.open(QFile.WriteOnly):
            QMessageBox.warning(self, \
                                self.tr \
                                ("Cant open file %1:\n%2").arg \
                                (self.srtfile3).arg(file.errorString()))

        if not self.srtfile4h.open(QFile.WriteOnly):
            QMessageBox.warning(self, \
                                self.tr \
                                ("Cant open file %1:\n%2").arg \
                                (self.srtfile4).arg(file.errorString()))

        self.srtstream4 = QTextStream(self.srtfile4h)
        self.logstream = QTextStream(self.logfileh)
        self.srtstream1 = QTextStream(self.srtfile1h)
        self.srtstream2 = QTextStream(self.srtfile2h)
        self.srtstream3 = QTextStream(self.srtfile3h)
            
        self.new_meta.emit(self.srtfile1,self.srtfile2,self.srtfile3,self.srtfile4)
        
    def isInitiated(self):
        return self.initiated

    def get_logfilename(self):
        return self.logfile

    def gen_new_outnames(self):
        srtoutpath = ("./Subtitles/"+self.cruiseid+"/"+self.loweringid.rstrip())
        txtoutpath = ("./Metadata/"+self.cruiseid+"/"+self.loweringid.rstrip())

        if not os.path.isdir(srtoutpath):
            print("New subtitle outpath " + srtoutpath) 
            pathlib.Path(srtoutpath).mkdir(parents=True, exist_ok=True)
        if not os.path.isdir(txtoutpath):
            print("New logfile outpath " + txtoutpath) 
            pathlib.Path(txtoutpath).mkdir(parents=True, exist_ok=True)

        nowstr = systime()
        self.logfile = '%s/%s%s' % (txtoutpath, nowstr, '.txt')
        self.srtfile1 = '%s/%s%s' % (srtoutpath, nowstr, '_st1.srt')
        self.srtfile2 = '%s/%s%s' % (srtoutpath, nowstr, '_st2.srt')
        self.srtfile3 = '%s/%s%s' % (srtoutpath, nowstr, '_st3.srt')
        self.srtfile4 = '%s/%s%s' % (srtoutpath, nowstr, '_st4.srt')
        
    def stop_logging(self):
        self.initiated = False
        self.close_outfiles()
        
    def get_metastr1(self):
        return self.metastr1

    def get_metastr2(self):
        return self.metastr2

    def get_metastr3(self):
        return self.metastr3

    def get_metastr4(self):
        return self.metastr4

    def parseJDS(self, jdspkt):
# "JDS 2012/04/13 16:52:39 JAS2 11.6877602 -58.5421899 851.68 6020.31 0.0 -3.2 244.02 1327.99 0.81 24356.0 -0.5."
        jdspkt.rstrip('\n')
        jdsfields  = jdspkt.split(" ")
        pktid = jdsfields[0]
        jdsdate = jdsfields[1]
        jdstime = jdsfields[2]
        veh = jdsfields[3]
        lat_deg = float(jdsfields[4])
        lon_deg = float(jdsfields[5])
        X_local = float(jdsfields[6])
        Y_local = float(jdsfields[7])
        oct_roll = float(jdsfields[8])
        oct_pitch = float(jdsfields[9])
        oct_heading = float(jdsfields[10])
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

        return veh,jdsdate,jdstime,lat_deg,lon_deg,X_local,Y_local,oct_roll,oct_pitch,oct_heading,depth,altitude

    def parseODR(self, odrpkt):
        # ODR 20120413 165239 JAS2 1.0 2.0 11 N001_McCue12 J2-000
        odrpkt.rstrip('\n')
        odrfields = odrpkt.split(" ")
        odrdatestr = odrfields[1]
        odrtimestr = odrfields[2]
        origlat = odrfields[4]
        origlon = odrfields[5]
        utmzone = odrfields[6]
        cruiseid = odrfields[7]
        lowid = odrfields[8]
        return odrdatestr, odrtimestr, origlat, origlon, utmzone, cruiseid, lowid

def systime():
    now = QDateTime.currentDateTime()
    systime = now.toString("yyyyMMddhhmmss.zz")
    return systime

def epoch_msecs():
    # Returns current time in milliseconds since epoch
    msec = QDateTime.currentMSecsSinceEpoch()
    return msec

def ms2srt_time_str(ms):
    '''
    Convert milliseconds to a string representing the time into the clip at
    which a subtitle is to be inserted, srt format.
    Copied from pysubtitles module found at oil21.org/~j/code/pysubtitles
    My thanks to that author.
    Given example (in ipython?)
    >>> ms2time(44592123)  yields 12:23:12,123
    '''
    it = int(ms /1000)
    ms = ms - it*1000
    ss = it % 60
    mm = ((it-ss)/60) % 60
    hh = ((it-(mm*60)-ss)/3600) % 60
    return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms)

    
