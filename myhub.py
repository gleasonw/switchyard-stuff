from switchyard.lib.userlib import *
import time


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
        removeTimedOut(forwarding_table, timeout)
        try:
            timestamp, input_port, packet = net.recv_packet()
            header = packet[0]
            destinationAddress = header.dst
            sourceAddress = header.src
            if destinationAddress in mymacs:
                pass
            elif destinationAddress in forwarding_table:
                properPort = forwarding_table[destinationAddress][0]
                sendSpecific(net, properPort, packet)
            else:
                sendAll(net, input_port, packet)
            if len(forwarding_table) >= max_storage:
                removeOneRule(forwarding_table)
            recordAddress(input_port, sourceAddress, forwarding_table, time.perf_counter())
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


# "learn" what puts are associated with what addresses
def recordAddress(inputPort, header, forwarding_table, timestamp):
    forwarding_table[header] = (inputPort, timestamp)


# remove from table after 30s to adapt to changes in network topology
def removeTimedOut(forwarding_table, timeout):
    for k in forwarding_table.keys():
        currentTimeStamp = forwarding_table.get(k)[1]
        timeDiff = int(abs(currentTimeStamp - time.perf_counter()))
        log_info(timeDiff)
        if timeDiff > timeout:
            log_info("Dropping entry {0}".format(k))
            forwarding_table.pop(k)


# determined by least recently used rule
def removeOneRule(forwarding_table):
    oldestAddress = min(forwarding_table.keys(), key=(lambda k: forwarding_table[k][1]))
    forwarding_table.pop(oldestAddress)
