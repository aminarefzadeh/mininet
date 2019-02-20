#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class MyTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self , n , **opt):
	switches = []
	for i in range(0,n):
		switches.append(self.addSwitch("s"+str(i)))
	host1 = self.addHost('h1')
	host2 = self.addHost('h2')
	
	for i in range(0,n-1):
		self.addLink( switches[i], switches[i+1], **opt)

	self.addLink( host1, switches[0], **opt)
	self.addLink( host2, switches[-1], **opt)


topos = { 	'topo1_1': ( lambda: MyTopo(2,**{"delay":"20ms"}) ),
			'topo1_2': ( lambda: MyTopo(2,**{"delay":"90ms"}) ),
			'topo2_1': ( lambda: MyTopo(2,**{"bw":1}) ),
			'topo2_2': ( lambda: MyTopo(2,**{"bw":15}) ),
			'topo3_1': ( lambda: MyTopo(2,**{"max_queue_size":1}) ),
			'topo3_2': ( lambda: MyTopo(2,**{"max_queue_size":15}) ),
			'topo4_1': ( lambda: MyTopo(2) ),
			'topo4_2': ( lambda: MyTopo(7) ) }

#sudo mn --custom q3.py --topo=mytopo --link=tc

