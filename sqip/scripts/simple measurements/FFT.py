import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'sqip/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 
import numpy as np

lattice = labrad.connect('192.168.169.254', password = 'lab')

minFreq = 18.2961*10**6#14.99885*10**6 #Hz
maxFreq = 18.3011*10**6#14.99887*10**6
recordTime = 0.5 #seconds
average = 50
saveFFT = True
#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
trfpga = cxn.timeresolvedfpga
trigger = cxn.trigger
trfpga.set_time_length(recordTime)
timeResolution = float(trfpga.get_resolution())
freqRes = 1.0 / recordTime
print lattice
dv = lattice.data_vault


freqs = np.arange(minFreq,maxFreq,freqRes)

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

import time####

pwr = np.zeros_like(freqs)
for i in range(average):
    print i
    trfpga.perform_time_resolved_measurement()
    time.sleep(.2)
    print 'now trigger'
    trigger.trigger('PaulBox')
    print 'now get result'
    timetags = trfpga.get_result_of_measurement().asarray
    print 'got timetags'
    pwr += getFFTpwr(timetags)
if saveFFT:
    dv.cd(['','QuickMeasurements','FFT'],True)
    dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
    data = np.array(np.vstack((freqs,pwr)).transpose().tolist(),dtype='float')
    print data
    #dv.add(data)
    fakedata = [[0.0,0.0],[0.1,0.1]]
    dv.add(data)
    
#import matplotlib.pyplot as plt
#
#fig= plt.figure()
#ax = fig.add_subplot(111)
#ax.plot(freqs,pwr,'-')
#plt.show()
print 'DONE'