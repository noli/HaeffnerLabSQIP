import sys; sys.path.append('C:\\Users\\expcontrol\\Desktop\\LabRAD\\sqip\\scripts')
import labrad
import numpy
import time
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

''' Ability to scan the detunings of both double passes and run two different pulse sequences:
RadialHeating.py for heating with radial beam (axial beam needed before and after for cooling)
or SoundVelocity.py where we specify start and stop time for each beam.'''

#Global parameters
comment = 'no comment'
iterations = 20
experimentName = 'HeatingRate'
heat_time = 0.3*1e6

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'comment':comment          
              }

pboxsequence = 'BackgroundHeatingRateMeas.py'

pboxDict = {
                'sequence':pboxsequence,
                'heat_time':heat_time
                }

recordTime = 0.100 + 0.050


#data processing on the fly
binTime =10.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)

parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
parameters.printDict()
#connect and define servers we'll be using
cxn = labrad.connect()
lattice = labrad.connect('192.168.169.254', password = 'lab')
dv = lattice.data_vault
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga


dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration, iterations)
        trfpga.perform_time_resolved_measurement()
        trigger.trigger('PaulBox')
        timetags = trfpga.get_result_of_measurement().asarray
        print timetags
        #saving timetags
        dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
        dv.new('timetags iter{0}'.format(iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
        dv.add_parameter('iteration',iteration)
        ones = numpy.ones_like(timetags)
        dv.add(numpy.vstack((timetags,ones)).transpose())
        #add to binning of the entire sequence
        newbinned = numpy.histogram(timetags, binArray )[0]
        binnedFlour = binnedFlour + newbinned
        time.sleep(1)  # corresponds to the cooling time between dark times. (1 sec lasercooling)
    print 'getting result and adding to data vault'
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)

print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
print 'DONE'
