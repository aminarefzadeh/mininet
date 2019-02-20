#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class MyTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self ):
	switch1 = self.addSwitch( 's1' )
	switch2 = self.addSwitch( 's2' )
	host1 = self.addHost('h1')
	host2 = self.addHost('h2')
	host3 = self.addHost('h3')
	host4 = self.addHost('h4')
	
	self.addLink( host1, switch1, delay='20ms')
	self.addLink( host2, switch1, delay='20ms')
	self.addLink( host3, switch2, delay='15ms')
	self.addLink( host4, switch2, delay='1s')
	self.addLink( switch1, switch2,delay='50ms')

#	self.addLink( switch1, switch2, bw=10, delay='5ms', loss=2,
#                          max_queue_size=1000, use_htb=True )
	
def perfTest():
    "Create network and run simple performance test"
    topo = MyTopo()
    net = Mininet( topo=topo, link=TCLink )
    net.start()
    print "Dumping host connections"
    dumpNodeConnections( net.hosts )
    print "Testing network connectivity"
    net.pingAll()
    print "Testing bandwidth between h1 and h4"
    h1, h4 = net.get( 'h1', 'h4' )
    result = h1.cmd("ping -c 1 "+h4.IP())
    print result
    #net.iperf( (h1, h4) )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()

topos = { 'mytopo': ( lambda: MyTopo() ) }

#sudo mn --custom q3.py --topo=mytopo --link=tc

