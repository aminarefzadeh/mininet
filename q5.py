#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class MyTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self ,n):
	switch = self.addSwitch( 's1' )
    hostes = []
    for i in range(0,n):
        host = self.addHost('h'+str(i))
	    hostes.append(host)
	    self.addLink( host, switch)
    	
def perfTest(n):
    "Create network and run simple performance test"
    topo = MyTopo(n)
    net = Mininet( topo=topo, link=TCLink )
    net.start()
    for i in range(0,n):
        host = net.get( 'h'+str(i) )
        host.cmd("python ping.py")
    

if __name__ == '__main__':
    setLogLevel( 'info' )
    n = input()
    perfTest(n)

#topos = { 'mytopo': ( lambda: MyTopo() ) }
#sudo mn --custom q3.py --topo=mytopo --link=tc

