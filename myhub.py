from switchyard.lib.userlib import *

def main(net):
    # constant: forwarding table size (int)
    # constant: timeout length in seconds (int)

    # add some informational text about ports on this device
    log_info ("Hub is starting up with these ports:")
    for port in net.ports():
        log_info ("{}: ethernet address {}".format(port.name, port.ethaddr))
        # make a list of our hub addresses so we drop requests coming to us
    #start timer
    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except Shutdown:
            # got shutdown signal
            break
        except NoPackets:
            # try again...
            continue

        # Check if destination in our list of hub addresses
            # If yes, drop it
            # if not, check if in our forwarding table
                # if yes, send it there and update forwarding table (different function?)
                # if not, broadcast
                    #sendAll(net, input_port)

        # new function SendToAll? Then SendSpecific(proper address)?
        # check if any entries have timed out

        # shutdown is the last thing we should do

        net.shutdown()

# send the packet out all ports *except*
# the one on which it arrived
def sendAll(net, inputPort, packet):
        for port in net.ports():
            if port.name != inputPort:
                net.send_packet(port.name, packet)

def sendSpecific(net, destPort, packet):
    net.send_packet(destPort, packet)



