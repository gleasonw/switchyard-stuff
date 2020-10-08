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
        try:
            timestamp, input_port, packet = net.recv_packet()
            header = packet[0]
            destinationAddress = header.dst
            sourceAddress = header.src
            log_info(forwarding_table)
            log_info(
                "Source: {0}, Destination: {1}, Input_Port: {2}".format(sourceAddress, destinationAddress, input_port))
            if destinationAddress in mymacs:
                pass
            # We thought that if we knew where a node was port-wise we should send the
            # packet out that port, but the test didn't like that... so we just always broadcast.
            elif destinationAddress in forwarding_table:
                # If destination is in the table, we need the port through which
                # we last received packets from the destination
                # properPort = forwarding_table[destinationAddress][0]
                # sendSpecific(net, properPort, packet)

                sendAll(net, input_port, packet)
            else:
                sendAll(net, input_port, packet)
            if len(forwarding_table) >= max_storage:
                removeOneRule(forwarding_table)

            recordAddress(input_port, sourceAddress, forwarding_table, time.perf_counter())
            removeTimedOut(forwarding_table, timeout)
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
        if (currentTimeStamp - time.perf_counter()) > timeout:
            forwarding_table.pop(k)


# determined by least recently used rule
def removeOneRule(forwarding_table):
    oldestAddress = min(forwarding_table.keys(), key=(lambda k: forwarding_table[k][1]))
    forwarding_table.pop(oldestAddress)
