from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer,QDateTime, QFile, QTextStream

import sys
import json
import random
import argparse
import datetime
import os
import time
import colorsys
import traceback
import threading

from pathlib import Path
import XPlaneUdp


LISTEN_PORT = 49005
SEND_PORT = 49000
XPLANE_IP = "192.168.0.18"


# Egna  funktioner
current_milli_time = lambda: int(round(time.time() * 1000))


parser = argparse.ArgumentParser()
parser.add_argument("--nogui", help="Run without GUI", action="store_true")
parser.add_argument("--file", help="Run selected file, use with --nogui")
args = parser.parse_args()
if args.nogui:
    GUI = False
    print("GUI turned off")
else:
    GUI = True



def signal_handler(sig, frame):
        print("You pressed Ctrl+C!")
        running = False
        sys.exit(0)
        os._exit(0)

def updateSlider(self, lamp, dataref, type=1):
    value = self.xp.getDataref(dataref,10)
    
    if (type == 1):
        value = value*100 + 100
    if (type == 2):
        value = value*100
    print("udpate slider", value)
    lamp.setValue(int(value))

def updateText(self, lamp, dataref):
    value = self.xp.getDataref(dataref,1)
    lamp.setText(str(int(value))+"%")

def updateLamp(self, lamp, dataref, color):
    if (self.xp.getDataref(dataref,2) >0):
        lamp.setStyleSheet("background-color: "+color)
    else:
        lamp.setStyleSheet("background-color: white")
    
def connectButton(self, button, dataref):
    button.pressed.connect(lambda: self.buttonPressed(dataref))
    button.released.connect(lambda: self.buttonReleased(dataref))
    
def connectOnButton(self, button, dataref):
    button.pressed.connect(lambda: self.buttonPressed(dataref))
def connectOffButton(self, button, dataref):
    button.pressed.connect(lambda: self.buttonReleased(dataref))

class RunGUI(QMainWindow):
    def __init__(self,):
        super(RunGUI,self).__init__()

        self.initUI()
        
        self.xp = XPlaneUdp.XPlaneUdp(XPLANE_IP,SEND_PORT)
        self.xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)

        self.xp.getDataref("JAS/autopilot/att",1)
        self.xp.getDataref("JAS/lamps/hojd",1)
        # self.xp.sendDataref("sim/cockpit/electrical/night_vision_on", 1)
        # 
        # self.xp.sendDataref("sim/cockpit/electrical/night_vision_on", 0)

        # 
        
        
    def initUI(self):
        #self.root = Tk() # for 2d drawing
        
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(current_dir, "../ui/main.ui"), self)
        print(self.ui)
        #self.setGeometry(200, 200, 300, 300)
        #self.resize(640, 480)
        self.setWindowTitle("JAS IS View")
        
        connectButton(self, self.ui.button_afk,"JAS/button/afk")
        connectButton(self, self.ui.button_hojd,"JAS/button/hojd")
        connectButton(self, self.ui.button_att,"JAS/button/att")
        connectButton(self, self.ui.button_spak,"JAS/button/spak")
        connectButton(self, self.ui.button_start,"JAS/button/start")
        
        
        connectOnButton(self, self.ui.button_apu_on,"JAS/button/apu")
        connectOffButton(self, self.ui.button_apu_off,"JAS/button/apu")
        connectOnButton(self, self.ui.button_ess_on,"JAS/button/ess")
        connectOffButton(self, self.ui.button_ess_off,"JAS/button/ess")
        connectOnButton(self, self.ui.button_hstrom_on,"JAS/button/hstrom")
        connectOffButton(self, self.ui.button_hstrom_off,"JAS/button/hstrom")
        connectOnButton(self, self.ui.button_lt_kran_on,"JAS/button/lt_kran")
        connectOffButton(self, self.ui.button_lt_kran_off,"JAS/button/lt_kran")
        
        self.ui.button_tanka.clicked.connect(self.buttonTankaFull)
        self.ui.button_tanka_50.clicked.connect(self.buttonTanka50)

        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(100)



    def updateGUI(self):
        # if (self.xp.dataList["JAS/lamps/hojd"] >0):
        #     self.ui.lamps_hojd.setStyleSheet("background-color: orange")
        # else:
        #     self.ui.lamps_hojd.setStyleSheet("background-color: white")
        updateLamp(self, self.ui.lamps_afk, "JAS/lamps/afk", "orange")
        updateLamp(self, self.ui.lamps_hojd, "JAS/lamps/hojd", "orange")
        updateLamp(self, self.ui.lamps_att, "JAS/lamps/att", "orange")
        updateLamp(self, self.ui.lamps_spak, "JAS/lamps/spak", "orange")
        
        updateLamp(self, self.ui.lamps_master1, "JAS/lamps/master1", "red")
        updateLamp(self, self.ui.lamps_master2, "JAS/lamps/master2", "red")
        
        updateLamp(self, self.ui.lamps_airbrake, "JAS/lamps/airbrake", "green")
        
        updateLamp(self, self.ui.buttonlamp_lt_kran, "JAS/button/lt_kran", "green")
        updateLamp(self, self.ui.lamps_apu_gar, "JAS/lamps/apu_gar", "green")
        updateLamp(self, self.ui.buttonlamp_apu, "JAS/button/apu", "green")
        updateLamp(self, self.ui.buttonlamp_hstrom, "JAS/button/hstrom", "green")
        updateLamp(self, self.ui.buttonlamp_ess, "JAS/button/ess", "green")
        
        
        updateText(self, self.ui.text_fuel, "JAS/fuel")
        updateSlider(self, self.ui.spak_roll, "sim/joystick/yoke_roll_ratio", type=2)
        updateSlider(self, self.ui.spak_pedaler, "sim/joystick/yoke_heading_ratio", type=2)
        updateSlider(self, self.ui.spak_pitch, "sim/joystick/yoke_pitch_ratio", type=2)
        updateSlider(self, self.ui.spak_gas, "sim/cockpit2/engine/actuators/throttle_ratio_all", type=2)
        
        
        
        pass
            
            
    def buttonPressed(self, dataref):
        print("buttonPressed:", dataref)
        self.xp.sendDataref(dataref, 1)
        
    def buttonReleased(self, dataref):
        print("buttonReleased:", dataref)
        self.xp.sendDataref(dataref, 0)   
             
    def buttonTankaFull(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 3000)
    def buttonTanka50(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 1500)
            
    def loop(self):
        self.xp.readData()
        self.updateGUI()
        
        #print(self.xp.dataList)
        self.timer.start(10)
        pass
        

if __name__ == "__main__":

    try:
        app = QApplication(sys.argv)
        win = RunGUI()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        print(traceback.format_exc())
        os._exit(1)
    print ("program end")
    os._exit(0)