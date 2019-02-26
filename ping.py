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
import traceback



if sys.platform.startswith("win32"):
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time


ICMP_ECHOREPLY = 0 # Echo reply (per RFC792)
ICMP_ECHO = 8 # Echo request (per RFC792)
ICMP_MAX_RECV = 2048  # Max size of incoming buffer


class Ping(object):

    def __init__(self):
        self.blacklist = {}
        self.myFile = {}
        self.wantedFile = {}  # "fileName" : [chumk1,chunk2,...]

    # --------------------------------------------------------------------------

    def header2dict(self, names, struct_format, data):
        """ unpack the raw received IP and ICMP header informations to a dict """
        unpacked_data = struct.unpack(struct_format, data)
        return dict(zip(names, unpacked_data))

    # --------------------------------------------------------------------------

    def send(self, current_socket,src,dst,data):
        # Create a new IP packet and set its source and destination IP addresses
        #print("sending from " + src + " to " + dst)
        #print("+++++++++++++++++++++++++++++")
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

    def build_file(self,filename):
        # check all piece gatehered and store file on ./myIP/filename and remove from wantedFile and myFile
        if filename not in self.wantedFile :
            print("panic: not wanted file")
            return
        else:
            chunks = self.wantedFile[filename]
            for chunk in chunks:
                if chunk == None:
                    print ("file not completed yet")
                    return
            else :
                data = ""
                for chunk in chunks:
                    data += chunk

                print(chunks)
                self.myFile.pop(filename)
                self.wantedFile.pop(filename)
                print ("data is : " + data)
                with open(IPrange + str(myIndex) + "_" + filename, "w") as recovered_file:
                    recovered_file.write(data)

    def handle_request(self,current_socket):
        data, packet_size, ip, ip_header, icmp_header = self.recieve(current_socket)
        if not icmp_header == 0 and icmp_header["type"]==ICMP_ECHOREPLY:
            lines = data.split()
            if (lines[0]=="return_home"):
                file_name = lines[1]
                home_ip = lines[2]
                if file_name not in self.myFile :
                    self.blacklist[file_name] = home_ip
                IP1, IP2 = findTwoRandomIP()
                time.sleep(2)
                self.send(current_socket, IP1, IP2, data)

            else:
                print("echo reply comes from " + ip)
                print("_______________________")
                file_name = lines[0]
                file_part = int(lines[1])

                if(lines[0] in self.blacklist):
                    #returning to home
                    time.sleep(2)
                    srcIP = self.blacklist[file_name]
                    self.send(current_socket,srcIP,findAnotherIP(srcIP),data)
                elif lines[0] in self.wantedFile :
                    index = data.find("\n") +1
                    index += data[index:].find("\n") +1
                    self.wantedFile[file_name][file_part] = data[index:]
                    self.build_file(file_name)
                else:
                    IP1, IP2 = findTwoRandomIP()
                    time.sleep(2)
                    self.send(current_socket, IP1, IP2, data)




    def handle_input(self,current_socket):
        command = raw_input()
        commands = command.split()
        if(commands[0]=="return_home"):
            print("return_home")
            file_name = commands[1]
            if file_name not in self.myFile:
                print("it's not your file")
                return
            payload = "return_home\n"+file_name+"\n"+IPrange+str(myIndex)
            IP1, IP2 = findTwoRandomIP()
            self.wantedFile[file_name]=[None for i in range(0,self.myFile[file_name])]
            self.send(current_socket, IP1, IP2, payload)


        if(commands[0]=="add"):
            file_name = commands[1]
            # data = commands[2]
            try:
                file_data = open(file_name, "r")
            except:
                print("file not exist!")
                return

            data = file_data.read()
            file_data.close()

            self.myFile[file_name] = (len(data)-1)/8 +1
            chunks = [data[i:i + 8] for i in range(0, len(data), 8)]
            for i in range(0,len(chunks)):
                payload = file_name + "\n" + str(i) + "\n" + chunks[i]
                IP1 , IP2 = findTwoRandomIP()
                time.sleep(0.5)
                self.send(current_socket,IP1,IP2,payload)
            print("file sended successfully")

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

        fd_to_object = {current_socket.fileno(): current_socket, sys.__stdin__.fileno(): sys.__stdin__}

        poller = select.poll()
        poller.register(current_socket, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        poller.register(sys.__stdin__, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        while True:
            try:
                events = poller.poll(0)
                for fd, flag in events:
                    if flag & (select.POLLIN | select.POLLPRI):
                        if (fd_to_object[fd] == current_socket):
                            self.handle_request(current_socket)
                        elif (fd_to_object[fd] == sys.__stdin__ ):
                            self.handle_input(current_socket)

                    elif flag & select.POLLHUP:
                        poller.unregister(fd_to_object[fd])
                    elif flag & select.POLLERR:
                        poller.unregister(fd_to_object[fd])
            except Exception as e:
                print("some thing happend")
                print (e.message)
                print (traceback.format_exc())
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

def findAnotherIP(srcIP):
    for i in range(1,hostNum+1):
        if(i!=myIndex):
            IP = IPrange+str(i)
            if(IP != srcIP):
                return IP



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
