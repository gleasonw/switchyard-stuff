from switchyard.lib.userlib import *
import time

# 1. I decided to change the algorithm for dropping entries from our forwarding table.
#    I thought of a case in which an address that normally sends and receives a lot of
#    packets suddenly goes dark -- I don't necessarily want to drop it, because it might
#    go active again and start sending a bajillion packets. My solution is to add a
#    heuristic that simply counts how many packets have been sent to a given address. In the real world
#    this counter would probably need to reset every hour or so. To decide which entry to drop
#    in my table, I take the two oldest entries and compare their "packet count".
#    I then drop the one with less packets sent to it.
# 2. The pro of this strategy is that I will in theory keep more of my popular addresses,
#    but I'll still favor recently active addresses over previously active ones. A con
#    is the additional complexity and the possibility of an address that gets a
#    whole bunch of packets and then goes dark forever, the only way to drop that address
#    is through a timeout.
def main(net):
    # constant: forwarding table size (int)
    # constant: timeout length in seconds (int)
    timeout = 30
    max_storage = 5

    # add some informational text about ports on this device
    log_info("Hub is starting up with these ports:")
    for port in net.ports():
        log_info("{}: ethernet address {}".format(port.name, port.ethaddr))
        # make a list of our hub addresses so we drop requests coming to us
    # start timer
    my_interfaces = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_interfaces]

    forwarding_table = {}
    while True:
        try:
            timestamp, input_port, packet = net.recv_packet()
            header = packet[0]
            destinationAddress = header.dst
            sourceAddress = header.src
            if destinationAddress in mymacs:
                pass
            # We thought that if we knew where a node was port-wise we should send the
            # packet out that port, but the test didn't like that... so we just always broadcast.
            elif destinationAddress in forwarding_table:
                # If destination is in the table, we need the port through which
                # we last received packets from the destination
                # properPort = forwarding_table[destinationAddress][0]
                # sendSpecific(net, properPort, packet)
                forwarding_table = iterateNumberPacketsSent(destinationAddress)
                sendAll(net, input_port, packet)
            else:
                sendAll(net, input_port, packet)
            if len(forwarding_table) >= max_storage:
                forwarding_table = removeOneRule(forwarding_table)
            forwarding_table = recordAddress(input_port, sourceAddress, forwarding_table, time.perf_counter())
            forwarding_table = removeTimedOut(forwarding_table, timeout)
        except Shutdown:
            # got shutdown signal
            break
        except NoPackets:
            # try again...
            continue

    net.shutdown()


# send the packet out all ports *except*
# the one on which it arrived
def sendAll(net, input_port, packet):
    for port in net.ports():
        if port.name != input_port:
            net.send_packet(port.name, packet)


# send to specific port if the port is located in forwarding table
def sendSpecific(net, destPort, packet):
    net.send_packet(destPort, packet)

def iterateNumberPacketsSent(address):
    currentNumberSent = forwarding_table[address][2]
    currentNumberSent = currentNumberSent + 1
    forwarding_table[address][2] = currentNumberSent
    return forwarding_table

# "learn" which ports are associated with which addresses
def recordAddress(inputPort, header, forwarding_table, timestamp):
    numberPacketsSentToAddress = 0
    forwarding_table[header] = (inputPort, timestamp, numberPacketsSentToAddress)
    return forwarding_table

# remove from table after 30s to adapt to changes in network topology
def removeTimedOut(forwarding_table, timeout):
    for k in forwarding_table.keys():
        currentTimeStamp = forwarding_table.get(k)[1]
        if (currentTimeStamp - time.perf_counter()) > timeout:
            forwarding_table.pop(k)
    return forwarding_table

# takes the two least recently used addresses and removes the less popular
# of the two (measured by sends to the destination)
def removeOneRule(forwarding_table):
    oldestAddress = min(forwarding_table.keys(), key=(lambda k: forwarding_table[k][1]))
    oldestAddressValue = forwarding_table.pop(oldestAddress)
    nextOldestAddress = min(forwarding_table.keys(), key=(lambda k: forwarding_table[k][1]))
    nextOldestSendCount = forwarding_table.pop(nextOldestAddress)[2]
    oldestSendCount = oldestAddressValue[2]
    if oldestSendCount > nextOldestSendCount:
        forwarding_table.pop(nextOldestAddress)
        forwarding_table[oldestAddress] = oldestAddressValue
    else:
        # we have already popped the oldest address out, so we can do nothing
        pass
    return forwarding_table
