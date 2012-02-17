"""
### BEGIN NODE INFO
[info]
name = CCTGUI
version = 1.1
description = Graphical user interface for DAC control,laser room and PMT count
instancename = CCTGUI
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 20
### END NODE INFO

"""



from PyQt4 import QtGui, QtCore

class CCT_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(CCT_GUI, self).__init__(parent)
        self.reactor = reactor

        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor)

        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(voltageControlTab,'&Trap V, DONT CHANGE FASTER THAN 1klick/s, otherwise reset DAC')
        tabWidget.addTab(lightControlTab,'&Laser Room')

        self.setCentralWidget(tabWidget)

    def makeLightWidget(self, reactor):
        widget = QtGui.QWidget()
        from CAVITY_CONTROL import cavityWidget
        from multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(cavityWidget(reactor),0,0)
        gridLayout.addWidget(multiplexerWidget(reactor),0,1)
        widget.setLayout(gridLayout)
        return widget

    def makeVoltageWidget(self, reactor):
        widget = QtGui.QWidget()
        from DAC_CONTROL import DAC_CONTROL
        from PMT_CONTROL import pmtWidget
        #from TRAPDRIVE_MODULATION_CONTROL import TRAPDRIVE_MODULATION_CONTROL
        from multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(DAC_CONTROL(reactor),0,0)
        gridLayout.addWidget(pmtWidget(reactor),0,1)
        #gridLayout.addWidget(TRAPDRIVE_MODULATION_CONTROL(reactor),1,0)
        
        widget.setLayout(gridLayout)
        return widget


    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    cctGUI = CCT_GUI(reactor)
    cctGUI.show()
    reactor.run()
