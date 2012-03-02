import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from qtui.QDACCalibrator import QDACCalibrator
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime

class DAC_CALIBRATOR(QDACCalibrator):
    def __init__(self, cxn, parent=None):
        self.dacserver = cxn.cctdac
        self.dmmserver = cxn.keithley_2100_dmm
        self.datavault = cxn.data_vault
        self.r = cxn.registry

        QDACCalibrator.__init__(self, parent)

        self.clicked = False # state of the "Calibrate" button

        # Connect functions
        # self.spinPower.valueChanged.connect(self.powerChanged)
        self.start.released.connect(self.buttonClicked)
    
    # This is where the magic happens
    def calib(self):
        
        #stepsize = 0b101010101
        totaltime = 1 #in hours 
        testvoltage = 0b101010101010101
        stepsize = 4 # seconds

        #self.digVoltages = range(0, 2**16, stepsize) # digital voltages we're going to iterate over
        timespan = range(0, 24, stepsize)
        anaVoltages = [] # corresponding analog voltages in volts
        self.dacserver.set_individual_digital_voltages([(int(self.channelToCalib), 0)])
        #time.sleep(1)
        for dv in self.timespan: # iterate over digital voltages

            self.dacserver.set_individual_digital_voltages([(int(self.channelToCalib), testvoltage)]) 

            time.sleep(stepsize*.5)
            
            av = self.dmmserver.get_dc_volts()

            time.sleep(stepsize*.5)
            #av = 0

            anaVoltages.append(av)
            print dv, "; ", av
        
        plt.figure(1)
        plt.plot(timespan, anaVoltages, 'ro')
        plt.show()


      #store in dataVault
        now = time.ctime()
        self.datavault.cd( ( ['DACCalibrations', 'timeline'], True ) )
        self.datavault.new( (now + ' single voltage over time', [('Time in seconds', 'num')], [('Volts','Analog Voltage','v')]) )
        arr = np.array([timespan, anaVoltages]).transpose().tolist()
        print arr
        print arr.dtype
        self.datavault.add( np.array([self.timespan, self.anaVoltages]).transpose().tolist() )

    def buttonClicked(self):
        self.channelToCalib = str(self.port.text())
        print self.channelToCalib
        
        self.clicked = True
        fit = self.calib() # Now calibrate

       
      
if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    dacserver = cxn.cctdac
    dmmserver = cxn.keithley_2100_dmm
    datavault = cxn.data_vault
    registry = cxn.registry
    dmmserver.select_device('GPIB Bus - USB0::0x05E6::0x2100::1243106')
    app = QtGui.QApplication(sys.argv)
    icon = DAC_CALIBRATOR(cxn)
    icon.show()
    app.exec_()
