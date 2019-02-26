#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
import time
import sys
import os
import select


class MyTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self ,n):
        switch = self.addSwitch( 's1' )
        for i in range(0,n):
            host = self.addHost('h'+str(i+1),)
            self.addLink( host, switch)


def perfTest(n):
    "Create network and run simple performance test"
    topo = MyTopo(n)
    net = Mininet( topo=topo, link=TCLink )
    net.start()
    for i in range(0,n):
        host = net.get( 'h'+str(i+1) )
        host.setIP('10.0.0.'+str(i+1))
    cli = CLI(net)
    net.stop()
        #host.sendCmd("python test.py "+"10.0.1."+" "+str(i+1)+" "+str(n))


# def perfTest(n):
#     "Create network and run simple performance test"
#     topo = MyTopo(n)
#     net = Mininet( topo=topo, link=TCLink )
#     net.start()
#     poller = select.poll()
#     fd_to_host = {}
#     for i in range(0,n):
#         host = net.get( 'h'+str(i) )
#         fd_to_host[host.stdout.fileno()] = host
#         host.setIP('10.0.1.'+str(i+1))
#         poller.register(host.stdout, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
#         host.sendCmd("python test.py "+str(i+1)+" "+str(n))
#
#     while True:
#         events = poller.poll(0)
#         for fd, flag in events:
#             host = fd_to_host[fd]
#             if flag & (select.POLLIN | select.POLLPRI):
#                 data = os.read(fd, 80000)
#                 if(data):
#                     print("from "+host.IP()+" :"+data)
#                 else:
#                     poller.unregister(host)
#             elif flag & select.POLLHUP:
#                 poller.unregister(host)
#             elif flag & select.POLLERR:
#                 poller.unregister(host)


if __name__ == '__main__':
    setLogLevel( 'info' )
    n = input()
    perfTest(n)

#topos = { 'mytopo': ( lambda: MyTopo() ) }
#sudo mn --custom q3.py --topo=mytopo --link=tc

