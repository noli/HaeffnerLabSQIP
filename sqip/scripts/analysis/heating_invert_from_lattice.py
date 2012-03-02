import labrad
import numpy as np
import matplotlib.pyplot as plt


experimentName = 'HeatingRateInvert'
iterations = 5
cool_time = 1*1e6 #mu seconds
prerecord = 50000.0 #mu seconds
sleep_time = 4.0 # seconds
recordTime = 0.100 + prerecord*10**-6
binTime =10.0*10**-6


binNumber = int(recordTime / binTime)
binArray = binTime * np.arange(binNumber + 1)
print binArray
binnedFlour = np.zeros(binNumber)



cxn = labrad.connect('192.168.169.254',password = 'lab')
dv = cxn.data_vault

dv.cd(['','Experiments',experimentName])

measurements = dv.dir()[0]
startmeasurement = measurements.index('2012Feb23_1123_09')
lastmeasurement = len(measurements)
folders = measurements[startmeasurement:-1]

for f in folders:
    

    dv.cd(['','Experiments',experimentName,f,'timetags'])
    iterations_available = dv.dir()[1]
    #print iterations_available
    
    for i in iterations_available:
        dv.open(i)
        timetag_2d = dv.get().asarray
        timetags = np.transpose(timetag_2d)[0]
        #print timetags
        newbinned = np.histogram(timetags, binArray )[0]
        #print newbinned
        binnedFlour = binnedFlour + newbinned
    
print binnedFlour


plt.plot(binnedFlour)
#plt.ylabel('some numbers')
plt.show()
    