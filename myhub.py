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
    time_table = {}
    while True:
        try:
            timestamp, input_port, packet = net.recv_packet()
        except Shutdown:
            # got shutdown signal
            break
        except NoPackets:
            # try again...
            continue

        header = packet[0]
        destinationAddress = header.dst

        # should we check for timedout entries here? or after we had new to table
        removeTimedOut(time_table, forwarding_table, timeout)

        if destinationAddress in mymacs:
            pass
        elif destinationAddress in forwarding_table:
            sendSpecific(net, destinationAddress, packet)
        else:
            sendAll(net, input_port, packet)

        if len(forwarding_table) >= max_storage:
            removeOneRule(forwarding_table)

        recordAddress(input_port, header.src, forwarding_table, time.perf_counter())

        # Check if destination in our list of hub addresses
        # If yes, drop it
        # if not, check if in our forwarding table
        # if yes, send it there and update forwarding table (different function?)
        # sendSpecific(net, destPort, packet)
        # recordTimestamp(header, time_table)
        # if not, broadcast
        # sendAll(net, input_port, packet)

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


# send to specific port if the port is located in forwarding table
def sendSpecific(net, destPort, packet):
    net.send_packet(destPort, packet)


# "learn" what puts are associated with what addresses
def recordAddress(inputPort, header, forwarding_table, timestamp):
    # check if it is has timedout
    forwarding_table.update(header, (inputPort, timestamp))


# remove from table after 30s to adapt to changes in network topology
def removeTimedOut(time_table, forwarding_table, timeout):
    for k, v in time_table:
        currentTimeStamp = forwarding_table.get(k)[1]
        if (currentTimeStamp - time.perf_counter()) > timeout:
            forwarding_table.pop(k)


# determined by least recently used rule
def removeOneRule(forwarding_table):
    oldestAddress = min(forwarding_table.keys(), key=(lambda k: forwarding_table[k][1]))
    forwarding_table.pop(oldestAddress)

    # oldest = max(time_table.values())
    # oldest_addr = []
    # for k,v in time_table:
    #     if v < oldest:
    #         oldest = v
    #         oldest_addr.insert[0] = k
    # forwarding_table.pop(oldest_addr[0])
    # time_table.pop(oldest_addr[0])
