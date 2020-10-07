from switchyard.lib.userlib import *
import time

def main(net):
    # constant: forwarding table size (int)
    # constant: timeout length in seconds (int)
    timeout = 30
    max_storage = 5

    # add some informational text about ports on this device
    log_info ("Hub is starting up with these ports:")
    for port in net.ports():
        log_info ("{}: ethernet address {}".format(port.name, port.ethaddr))
        # make a list of our hub addresses so we drop requests coming to us
    #start timer
    my_interfaces = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_interfaces]

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
        removeTimedOut(time_table, forwarding_table, timeout)

        if header.dst in mymacs:
            pass #drop it
        elif header.dst in forwarding_table:
            sendSpecific(net, header.dst, packet)
            if (len(forwarding_table < max_storage)):
                removeOneRule(forwarding_table, time_table)
            recordTimestamp(header.dst, time_table)
        else:
            sendAll(net, input_port, packet)
        
        if header.src not in forwarding_table:
            recordAddress(input_port, header.src, forwarding_table, time_table)



        # Check if destination in our list of hub addresses
            # If yes, drop it
            # if not, check if in our forwarding table
                # if yes, send it there and update forwarding table (different function?)
                    #sendSpecific(net, destPort, packet)
                    #recordTimestamp(header, time_table)
                # if not, broadcast
                    #sendAll(net, input_port, packet)

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
    forwarding_table.update(header, port)
    recordTimestamp(header, time_table)

def recordTimestamp(header, time_table):
    time_table.update(header, time.perf_counter())

#remove from table after 30s to adapt to changes in network topology
def removeTimedOut(time_table, forwarding_table, timeout):
    for k,v in time_table:
        if (time_table.get(k) - time.perf_counter()) > timeout:
            forwarding_table.pop(k)
            time_table.pop(k)

#determined by least recently used rule
def removeOneRule(forwarding_table, time_table):
    oldest = 2147483647
    oldest_addr = []
    for k,v in time_table.keys():
        if v < oldest:
            oldest = v
            oldest_addr.insert[0] = k
    forwarding_table.pop(oldest_addr[0])
    time_table.pop(oldest_addr[0])





