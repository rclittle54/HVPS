#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:04:23 2019

@author: ryanlittle


High Voltage Power Supply GUI - LoCoLab Spring 2019





"""

# Import statements
from os import path, chdir
from tkinter import Label, StringVar, Entry, Button, Listbox, END, Menu, Toplevel, Tk, _tkinter, IntVar, Spinbox, Radiobutton, DISABLED
import tkinter.filedialog as fd
from tkinter import messagebox

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time

import serial

import numpy as np

# ==================================================================
# ==================================================================
# ==================================================================
# This is needed to allow for proper importing of default data files
import sys
if getattr(sys,'frozen',False):
    application_path = path.dirname(sys.executable)
    chdir(application_path)
# ==================================================================
# ==================================================================    
# ==================================================================








# GUI Parameters
PLOTRATIO = (4,2.5)
PLOTDPI = 100
LABELFONT = ("Arial",20,"bold")
REFRESH_FREQ = 5 # Every this many milliseconds




#%%

#def StairStep(H,W,n):
#    x = np.arange(0,W*n,1/(1000*REFRESH_FREQ))
#    y = np.zeros(len(x))
#    for i,val in enumerate(x):
#        current_step = int(val)/int(W)
#        y[i] = current_step*H
#    return (x,y)



# SUPER BUGGY for some reason, be careful!
#def StairStep(H,W,n):
#    y = []
#    for rep in range(1,n+1):
#        reprange = np.arange(0,W,1/(1000*REFRESH_FREQ))
#        y += [rep*H for i in reprange]
#    x = np.arange(0,len(y),1/(1000*REFRESH_FREQ))
#    return (x,y)
        

SIGNALCONSTANT = 1

def StairStep(H,W,n):
    x = np.arange(0,n*W,1/(SIGNALCONSTANT*REFRESH_FREQ))
    y = []
    for i in x:
        y += [H*(np.floor(i/W)+1)]
    return (x,y)



def Step(H,W,n):
    x = np.arange(0,2*W*n,1/(SIGNALCONSTANT*REFRESH_FREQ))
    y = []
    for rep in range(n):
        reprange = np.arange(0,W,1/(SIGNALCONSTANT*REFRESH_FREQ))
        y += [H for i in reprange]
        y += [0 for i in reprange]
    
    return (x,y)

def Sawtooth(H,W,n):
    x = np.arange(0,n*W,1/(SIGNALCONSTANT*REFRESH_FREQ))
    y = []
    for rep in range(n):
        rep_range = np.arange(0,W,1/(SIGNALCONSTANT*REFRESH_FREQ))
        #rep_y = (H/W)*rep_range
        y += [(H/W)*i for i in rep_range]
    
    
    return (x,y)


#%%

def GetSerial():
    pass


class HVPS:
    def __init__(self,master):
        self.master = master
        master.title("LoCoLab HVPS Console")
        
        self.ser = None
        
        LCOL = 0
        RCOL = 4
        
        # Critical parameters
        #self.CURRENTVOLTAGE = IntVar(master,value=0)
        #self.TARGETVOLTAGE = IntVar(master,value=0)
        #self.PWM = IntVar(master,value=0)
        self.CURRENTVOLTAGE = StringVar(master,value='0')
        self.TARGETVOLTAGE = StringVar(master,value='0')
        self.PWM = StringVar(master,value='30')
        
        
        self.IS_SERIAL_CONNECTED = False
        
        # Plotting parameters
        self.npoints = 240
        self.current_line = [0 for x in range(self.npoints)]
        self.target_line = [0 for x in range(self.npoints)]
        
        
        # Plots ===============================================================
        self.f1 = plt.figure(figsize=PLOTRATIO,dpi=PLOTDPI)
        self.a1 = self.f1.add_subplot(111)
        self.a1.grid()
        self.a1.set_title("Voltage")
        self.canvas1 = FigureCanvasTkAgg(self.f1,master)
        self.canvas1.get_tk_widget().grid(sticky='W',row=0,rowspan=5,column=LCOL+0,columnspan=RCOL)
        
        self.f2 = plt.figure(figsize=PLOTRATIO,dpi=PLOTDPI)
        self.a2 = self.f2.add_subplot(111)
        self.a2.grid()
        self.a2.set_title("PWM")
        self.canvas2 = FigureCanvasTkAgg(self.f2,master)
        self.canvas2.get_tk_widget().grid(sticky='W',row=6,rowspan=1,column=LCOL+0,columnspan=RCOL)
        
        self.f3 = plt.figure(figsize=PLOTRATIO,dpi=PLOTDPI)
        self.a3 = self.f3.add_subplot(111)
        self.a3.grid()
        self.a3.set_title("Signal")
        self.canvas3 = FigureCanvasTkAgg(self.f3,master)
        self.canvas3.get_tk_widget().grid(sticky='W',row=6,rowspan=1,column=RCOL+1,columnspan=7)
        self.a3_xlim = 0
        self.a3_ylim = 0
        
        
        # Labels ==============================================================
        self.currentlabel = Label(master,text="Current:",font=LABELFONT)
        self.currentlabel.grid(row=0,column=RCOL+1)
        self.dynamic_currentlabel = Label(master,textvar=self.CURRENTVOLTAGE,font=LABELFONT)
        self.dynamic_currentlabel.grid(row=0,column=RCOL+2,sticky='W')
        self.currentunitslabel = Label(master,text="kV")
        self.currentunitslabel.grid(row=0,column=RCOL+3,sticky='W')
        
        self.targetlabel = Label(master,text="Target:",font=LABELFONT)
        self.targetlabel.grid(row=1,column=RCOL+1)
        self.dynamic_targetlabel = Label(master,textvar=self.TARGETVOLTAGE,font=LABELFONT)
        self.dynamic_targetlabel.grid(row=1,column=RCOL+2,sticky='W')
        self.targetunitslabel = Label(master,text="kV")
        self.targetunitslabel.grid(row=1,column=RCOL+3,sticky='W')
        
        self.pwmlabel = Label(master,text="PWM:",font=LABELFONT)
        self.pwmlabel.grid(row=2,column=RCOL+1)
        self.dynamic_pwmlabel = Label(master,textvar=self.PWM,font=LABELFONT)
        self.dynamic_pwmlabel.grid(row=2,column=RCOL+2,sticky='W')
        self.pwmunitslabel = Label(master,text="/ 1023")
        self.pwmunitslabel.grid(row=2,column=RCOL+3,sticky='W')
        
        
        
        # Target Voltage Input ================================================
        self.targetvoltageentrystr = StringVar(master,value='0')
        self.targetvoltageentry = Entry(master,textvar=self.targetvoltageentrystr)
        self.targetvoltageentry.grid(row=1,column=RCOL+4)
        
        self.targetvoltagesendbutton = Button(master,text="Send",command=self.SendVoltage)
        self.targetvoltagesendbutton.grid(row=1,column=RCOL+5)
        
        
        
        # Signal ==============================================================
#        self.signallabel = Label(master,text="Signal:")
#        self.signallabel.grid(row=3,column=1)
        
        self.IS_SENDING_SIGNAL = False
        
        self.signalx = []
        self.signaly = []
        
        self.signallistbox = Listbox(master,height=2)
        self.signallistbox.insert(1,"Step")
        self.signallistbox.insert(2,"Stairstep")
        self.signallistbox.insert(3,"Sawtooth")
        self.signallistbox.grid(sticky='E',row=7,column=RCOL+1,columnspan=2)
        
        self.amplitudelabel = Label(master,text="Amplitude:")
        self.amplitudelabel.grid(row=8,column=RCOL+1)
        self.amplitudeentrystr = StringVar(master,value='0.5')
        self.amplitudeentry = Entry(master,textvar=self.amplitudeentrystr)
        self.amplitudeentry.grid(row=8,column=RCOL+2,columnspan=2)
        self.amplitudeunitslabel = Label(master,text="kV")
        self.amplitudeunitslabel.grid(row=8,column=RCOL+4)
        
        self.dwelltimelabel = Label(master,text="Dwell time:")
        self.dwelltimelabel.grid(row=9,column=RCOL+1)
        self.dwelltimeentrystr = StringVar(master,value='30')
        self.dwelltimeentry = Entry(master,textvar=self.dwelltimeentrystr)
        self.dwelltimeentry.grid(row=9,column=RCOL+2,columnspan=2)
        self.dwelltimeunitslabel = Label(master,text="sec")
        self.dwelltimeunitslabel.grid(row=9,column=RCOL+4)
        
        self.nrepslabel = Label(master,text="# Reps:")
        self.nrepslabel.grid(row=10,column=RCOL+1)
        self.nrepsspinbox = Spinbox(master,from_=0,to_=50)
        self.nrepsspinbox.grid(row=10,column=RCOL+2,columnspan=2)
        
        self.updatesignalbutton = Button(master,text="Update",command=self.UpdateSignalButton)
        self.updatesignalbutton.grid(row=11,column=RCOL+1)
        
        self.executesignalbutton = Button(master,text="Execute",command=self.ExecuteSignalButton)
        self.executesignalbutton.grid(row=11,column=RCOL+2)
        
        
        
        
        # Serial port =========================================================
        self.seriallabel = Label(master,text="Serial Port")
        self.seriallabel.grid(sticky='W',row=7,column=0)
        
        self.serialentrystr = StringVar(master,value='/dev/cu.wchusbserial1420')
        self.serialentry = Entry(master,textvar=self.serialentrystr)
        self.serialentry.grid(sticky='W',row=7,column=1)
        
        self.serialconnectbutton = Button(master,text="Connect",command=self.ConnectToSerial)
        self.serialconnectbutton.grid(sticky='W',row=7,column=2)
        
        self.baudratelabel = Label(master,text="Baud Rate")
        self.baudratelabel.grid(sticky='W',row=8,column=0)
        
        self.baudrateentrystr = StringVar(master,value='115200')
        self.baudrateentry = Entry(master,textvar=self.baudrateentrystr)
        self.baudrateentry.grid(sticky='W',row=8,column=1)
        
        
        # Data Logging ========================================================
        self.loglabel = Label(master,text="Data Logging")
        self.loglabel.grid(sticky='W',row=9,column=0)
        
        self.logfnameentrystr = StringVar(master,value='SessionLog.txt')
        self.logfnameentry = Entry(master,textvar=self.logfnameentrystr)
        self.logfnameentry.grid(sticky='W',row=9,column=1)
        
        self.logging_variable = IntVar(master,value=0)
        self.logging_offbutton = Radiobutton(master,text="Off",variable=self.logging_variable,value=0,width=4)
        self.logging_offbutton.grid(row=9,column=2)
        
        self.logging_onbutton = Radiobutton(master,text="On",variable=self.logging_variable,value=1,width=4)
        self.logging_onbutton.grid(row=9,column=3)
        
        
        
        # Abort ===============================================================
        self.abortbutton = Button(master,text="ABORT",command=self.ABORT)
        self.abortbutton.grid(row=11,column=0)
        
        return
    
    def DoNothing(self):
        pass
    
    
    
    def SendVoltage(self,sendv=0):
        try:
            V = float(self.targetvoltageentrystr.get())
            if sendv != 0:
                V = sendv
            self.TARGETVOLTAGE.set(str(V))
            
            w_str = "%f\n"%(V) # Format to send voltage
            
            
            self.ser.write(w_str.encode())
        except Exception as e:
            print("ERROR: %s"%(e))
        return
    
    
    def ConnectToSerial(self):
        try:
            port = self.serialentrystr.get()
            baudrate = int(self.baudrateentrystr.get())
            print("Trying to connect to %s at %d"%(port,baudrate))
            self.ser = serial.Serial(port,baudrate)
            self.ser.flushInput()
        except ValueError:
            print("ERROR: Invalid serial parameter.")
            return -1
        except:
            print("Error")
            return -1
        
        print("Success.")
        
        self.IS_SERIAL_CONNECTED = True
        self.GetSerialValue()
        
        return
    
    
    def GetSerialValue(self):
        if not self.IS_SERIAL_CONNECTED:
            #self.master.after(50,self.GetSerialValue)
            return
        try:
            # Grab data
            rawdata = self.ser.readline().decode('utf8')
            # Parse data
            currentval = float(rawdata.split(' ')[0])
            targetval = float(self.TARGETVOLTAGE.get())
            self.CURRENTVOLTAGE.set(str(currentval))
            if self.logging_variable.get() == 1: self.LogData([targetval,currentval])
            
            
            # Append data, shift over lines
            self.current_line.append(currentval)
            self.current_line = self.current_line[1:self.npoints+1]
            self.target_line.append(targetval)
            self.target_line = self.target_line[1:self.npoints+1]
            
            
            if self.IS_SENDING_SIGNAL:
                if len(self.signaly) == 0:
                    self.IS_SENDING_SIGNAL = False
                else:
                    #print("Sending signal: %f, next is "%(self.signaly[0]),end="")
                    #self.SendVoltage(self.signaly[0])
                    v = self.signaly[0]
                    self.TARGETVOLTAGE.set("%f"%(v))
                    wstr = "%f\n"%(v)
                    self.ser.write(wstr.encode())
                    self.signaly = self.signaly[1:]
                    self.signalx = self.signalx[:-1]
                    #print("%f"%(self.signaly[0]))
                    
                    self.a3.clear()
                    self.a3.plot(self.signalx,self.signaly,color='tab:blue')
                    self.a3.set_title("Signal")
                    self.a3.set_xlim(0,self.a3_xlim)
                    self.a3.set_ylim(0,self.a3_ylim)
                    self.a3.grid()
                    self.canvas3.draw()
            
            
            
            self.master.after_idle(self.PlotLine)
        except Exception as e:
            print(e)
        
        self.master.after(REFRESH_FREQ,self.GetSerialValue)
        
        
        
        return
    
    def PlotLine(self):
        #max_val = max(self.current_line) + 1e-5 # Include extra for padding?
        self.a1.clear()
        self.a1.plot(self.current_line,color='tab:blue',label='Actual')
        self.a1.plot(self.target_line,color='tab:green',linestyle=':',label='Target')
        self.a1.grid()
        self.a1.legend(loc=3)
        self.a1.set_ylim(-1.5,1.5)
        self.canvas1.draw()
        #print("Beep")
        
        
        
        return
    
    
    def UpdateSignalButton(self):
        try:
            selected_signal = self.signallistbox.curselection()[0]
        except:
            print("No selection!")
            return
            
        #print(selected_signal)
        try:
            H = float(self.amplitudeentrystr.get())
            W = float(self.dwelltimeentrystr.get())
            n = int(self.nrepsspinbox.get())
        except ValueError:
            print("ERROR: Invalid signal parameter.")
            return
        
        if selected_signal == 0:
            # Step case
            self.signalx, self.signaly = Step(H,W,n)
        
        elif selected_signal == 1:
            self.signalx, self.signaly = StairStep(H,W,n)
            
        elif selected_signal == 2:
            self.signalx, self.signaly = Sawtooth(H,W,n)
        
        
        
        # Plot to a3
        self.a3_xlim = max(self.signalx)
        self.a3_ylim = max(self.signaly)*1.2
        self.a3.clear()
        self.a3.plot(self.signalx,self.signaly,color='tab:blue')
        self.a3.set_title("Signal")
        self.a3.set_xlim(0,self.a3_xlim)
        self.a3.set_ylim(0,self.a3_ylim)
        self.a3.grid()
        self.canvas3.draw()
        
        
        return
    
    def ExecuteSignalButton(self):
        self.IS_SENDING_SIGNAL = True
        self.targetvoltagesendbutton.state = DISABLED
        print("Beep")
        
        return
    
    def mainloop(self):
        self.master.mainloop()
        return
    
    
    
    def LogData(self,data):
        fname = self.logfnameentrystr.get()
        f = open(fname,'a')
        writestr = ''
        for d in data:
            writestr += "%f,"%(d)
        
        writestr = writestr[:-1]+'\n'
        f.write(writestr)
        f.close()
        
        return
    
    
    def OnUpdate(self):
        pass
    
    
    def OnExecute(self):
        pass
    
    def ABORT(self):
        self.IS_SERIAL_CONNECTED = False
        self.TARGETVOLTAGE.set('0')
        self.IS_SENDING_SIGNAL = False
        self.signalx = []
        self.signaly = []
        
        return








if __name__ == '__main__':
    root = Tk()
    useGUI = HVPS(root)
    #useGUI.GetSerialValue()
    useGUI.mainloop()

