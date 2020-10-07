from switchyard.lib.userlib import *
import datetime

def main(net):
    # constant: forwarding table size (int)
    # constant: timeout length in seconds (int)

    # add some informational text about ports on this device
    log_info ("Hub is starting up with these ports:")
    for port in net.ports():
        log_info ("{}: ethernet address {}".format(port.name, port.ethaddr))
        # make a list of our hub addresses so we drop requests coming to us
    #start timer
    forwarding_table = {}
    time_table = {}
    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except Shutdown:
            # got shutdown signal
            break
        except NoPackets:
            # try again...
            continue

        header = packet[0]

        #should we check for timedout entries here? or after we had new to table
        removeTimedOut(time_table, forwarding_table)

        # Check if destination in our list of hub addresses
            # If yes, drop it
            # if not, check if in our forwarding table
                # if yes, send it there and update forwarding table (different function?)
                    #send
                    #recordTimestamp(header, time_table)
                # if not, broadcast
                    #sendAll(net, input_port)

        # new function SendToAll? Then SendSpecific(proper address)?
        # check if any entries have timed out

        # shutdown is the last thing we should do

        net.shutdown()

# send the packet out all ports *except*
# the one on which it arrived
def sendAll(net, input_port, packet):
        for port in net.ports():
            if port.name != input_port:
                net.send_packet(port.name, packet)

def sendSpecific(net, destPort, packet):
    net.send_packet(destPort, packet)

def recordAddress(port, header, forwarding_table, time_table):
    #check if it is has timedout
    forwarding_table.update(header.dst, port)
    recordTimestamp(header, time_table)

def recordTimestamp(header, time_table):
    time_table.update(header.dst, datetime.datetime.now().time())

def removeTimedOut(time_table, forwarding_table):
    for k,v in time_table:
        if time_table.get(k) - datetime.datetime.now().time > 30:
            forwarding_table.pop(k)

