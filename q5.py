#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import time
import sys
import os
import select


class MyTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self ,n):
        switch = self.addSwitch( 's1' )
        for i in range(0,n):
            host = self.addHost('h'+str(i),)
            self.addLink( host, switch)

def perfTest(n):
    "Create network and run simple performance test"
    topo = MyTopo(n)
    net = Mininet( topo=topo, link=TCLink )
    net.start()
    poller = select.poll()
    fd_to_host = {}
    for i in range(0,n):
        host = net.get( 'h'+str(i) )
        fd_to_host[host.stdout.fileno()] = host
        host.setIP('10.0.1.'+str(i+1))
        poller.register(host.stdout, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        host.sendCmd("python test.py "+str(i+1)+" "+str(n))




    while True:

        # Wait for at least one of the sockets to be ready for processing
        events = poller.poll(0)

        for fd, flag in events:
            host = fd_to_host[fd]
            if flag & (select.POLLIN | select.POLLPRI):
                data = os.read(fd, 80000)
                if(data):
                    print("from "+host.IP()+" :"+data)
                else:
                    poller.unregister(host)
            elif flag & select.POLLHUP:
                poller.unregister(host)
            elif flag & select.POLLERR:
                poller.unregister(host)

    # while(True):
    #     i=0
    #     host = net.get( 'h'+str(i) )
    #     fd, event = host.waitReadable(timeoutms=1000)[0]
    #     if(event!=4):
    #         print(event)
    #         print(os.read(fd,200))
    #         host.terminate()
    #         break
    #     if(host.waiting == False):
    #         host.terminate()
    #         break

    

if __name__ == '__main__':
    setLogLevel( 'info' )
    n = input()
    perfTest(n)

#topos = { 'mytopo': ( lambda: MyTopo() ) }
#sudo mn --custom q3.py --topo=mytopo --link=tc

