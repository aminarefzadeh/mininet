"""
	A pure python ping implementation using raw sockets.

	Note that ICMP messages can only be send from processes running as root
	
"""

import os
import select
import signal
import struct
import sys
import time
import socket, sys
from impacket import ImpactPacket
import select

if sys.platform.startswith("win32"):
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

# ICMP parameters
ICMP_ECHOREPLY = 0  # Echo reply (per RFC792)
ICMP_ECHO = 8  # Echo request (per RFC792)
ICMP_MAX_RECV = 2048  # Max size of incoming buffer

MAX_SLEEP = 1000


def is_valid_ip4_address(addr):
    parts = addr.split(".")
    if not len(parts) == 4:
        return False
    for part in parts:
        try:
            number = int(part)
        except ValueError:
            return False
        if number > 255 or number < 0:
            return False
    return True


def to_ip(addr):
    if is_valid_ip4_address(addr):
        return addr
    return socket.gethostbyname(addr)


class Response(object):
    def __init__(self):
        self.max_rtt = None
        self.min_rtt = None
        self.avg_rtt = None
        self.packet_lost = None
        self.ret_code = None
        self.output = []

        self.packet_size = None
        self.timeout = None
        self.source = None
        self.destination = None
        self.destination_ip = None


class Ping(object):

    # --------------------------------------------------------------------------

    def signal_handler(self, signum, frame):
        """
		Handle print_exit via signals
		"""
        self.print_exit()
        msg = "\n(Terminated with signal %d)\n" % (signum)

        if self.quiet_output:
            self.response.output.append(msg)
            self.response.ret_code = 0
        else:
            print(msg)

        sys.exit(0)

    def setup_signal_handler(self):
        signal.signal(signal.SIGINT, self.signal_handler)  # Handle Ctrl-C
        if hasattr(signal, "SIGBREAK"):
            # Handle Ctrl-Break e.g. under Windows
            signal.signal(signal.SIGBREAK, self.signal_handler)

    # --------------------------------------------------------------------------

    def header2dict(self, names, struct_format, data):
        """ unpack the raw received IP and ICMP header informations to a dict """
        unpacked_data = struct.unpack(struct_format, data)
        return dict(zip(names, unpacked_data))

    # --------------------------------------------------------------------------

    def run(self, count=None, deadline=None):
        """
		send and receive pings in a loop. Stop if count or until deadline.
		"""
        if not self.quiet_output:
            self.setup_signal_handler()

        while True:
            delay = self.do()

            self.seq_number += 1
            if count and self.seq_number >= count:
                break
            if deadline and self.total_time >= deadline:
                break

            if delay == None:
                delay = 0

            # Pause for the remainder of the MAX_SLEEP period (if applicable)
            if (MAX_SLEEP > delay):
                time.sleep((MAX_SLEEP - delay) / 1000.0)

        self.print_exit()
        if self.quiet_output:
            return self.response

    def send(self, current_socket,src,dst,data):
        # Create a new IP packet and set its source and destination IP addresses
        print("sending from " + src + " to " + dst)
        print("+++++++++++++++++++++++++++++")
        ip = ImpactPacket.IP()
        ip.set_ip_src(src)
        ip.set_ip_dst(dst)
        # Create a new ICMP ECHO_REQUEST packet
        icmp = ImpactPacket.ICMP()
        icmp.set_icmp_type(icmp.ICMP_ECHO)
        # inlude a small payload inside the ICMP packet
        # and have the ip packet contain the ICMP packet
        icmp.contains(ImpactPacket.Data(data))
        ip.contains(icmp)
        # give the ICMP packet some ID
        icmp.set_icmp_id(0x03)
        # set the ICMP packet checksum
        icmp.set_icmp_cksum(0)
        icmp.auto_checksum = 1
        # send the provided ICMP packet over a 3rd socket
        try:
            current_socket.sendto(ip.get_packet(), (dst, 1))  # Port number is irrelevant for ICMP
        except socket.error as e:
            return

    def recieve(self, current_socket):
        packet_data, address = current_socket.recvfrom(ICMP_MAX_RECV)
        icmp_header = self.header2dict(
            names=[
                "type", "code", "checksum",
                "packet_id", "seq_number"
            ],
            struct_format="!BBHHH",
            data=packet_data[20:28]
        )
        # if icmp_header["packet_id"] == self.own_id: # Our packet!!!
        # it should not be our packet!!!Why?
        ip_header = self.header2dict(
            names=[
                "version", "type", "length",
                "id", "flags", "ttl", "protocol",
                "checksum", "src_ip", "dest_ip"
            ],
            struct_format="!BBHHHBBHII",
            data=packet_data[:20]
        )
        packet_size = len(packet_data) - 28
        ip = socket.inet_ntoa(struct.pack("!I", ip_header["src_ip"]))
        data = packet_data[28:]
        # XXX: Why not ip = address[0] ???
        return data, packet_size, ip, ip_header, icmp_header

    def handle_request(self,current_socket):
        data, packet_size, ip, ip_header, icmp_header = self.recieve(current_socket)
        if ip_header["ttl"]== 64:
            print("echo reply comes from "+ip)
            print("_______________________")
            IP1, IP2 = findTwoRandomIP()
            time.sleep(2)
            self.send(current_socket, IP1, IP2, data)

        if ip_header["ttl"]== 225:
            print("echo request comes from "+ip)
            print("_______________________")



    def handle_input(self,current_socket):
        command = raw_input()
        print(command)
        commands = command.split()
        if(commands[0]=="return_home"):
            print("return home")
            file_name = commands[1]
            dest_name = commands[2]

        if(commands[0]=="add"):
            file_name = commands[1]
            data = commands[2]
            payload = file_name + "\n" + "1" + "\n" + data
            IP1 , IP2 = findTwoRandomIP()
            self.send(current_socket,IP1,IP2,payload)

    def server(self):
        try:
            current_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            current_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            # Bind the socket to a source address
            #current_socket.bind((None,0))  # Port number is irrelevant for ICMP


        except socket.error, (errno, msg):
            if errno == 1:
                # Operation not permitted - Add more information to traceback
                # the code should run as administrator
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    "%s - Note that ICMP messages can only be sent from processes running as root." % evalue
                )
                raise etype, evalue, etb
            raise  # raise the original error

        fd_to_object = {}
        fd_to_object[current_socket.fileno()]= current_socket
        fd_to_object[sys.__stdout__.fileno()]= sys.__stdout__
        poller = select.poll()
        poller.register(current_socket, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        poller.register(sys.__stdout__, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        while True:
            try:
                events = poller.poll(0)
                for fd, flag in events:
                    if flag & (select.POLLIN | select.POLLPRI):
                        if (fd_to_object[fd] == current_socket):
                            self.handle_request(current_socket)
                        else:
                            self.handle_input(current_socket)

                    elif flag & select.POLLHUP:
                        poller.unregister(fd_to_object[fd])
                    elif flag & select.POLLERR:
                        poller.unregister(fd_to_object[fd])
            except:
                print("some thing happend")
                current_socket.close()
                return




import sys
from random import random

IPrange = sys.argv[1]
myIndex = int(sys.argv[2])
hostNum = int(sys.argv[3])


def findTwoRandomIP():
    selected1 = int(random()*(hostNum-1))+1
    selected2 = int(random()*(hostNum-2))+1
    if selected1>= myIndex:
        selected1+=1
        if(selected2>=myIndex):
            selected2+=1
        if(selected2>=selected1):
            selected2+=1
    else:
        if (selected2 >= selected1):
            selected2 += 1
        if (selected2 >= myIndex):
            selected2 += 1

    return (IPrange+str(selected1),IPrange+str(selected2))


p = Ping()
p.server()


# commands --> return_home
# commands --> add name_of_file

# making appropriate data and reading and chunking files and put data on body
# reciving data countinuesly and with select reading from stdin to for commands. after recieving ping to random location

# command = raw_input()
# # if command == "return_home":
# IP1 = "10.0.0.2"
# IP2 = "10.0.0.3"
# ping(IP1, IP2)
