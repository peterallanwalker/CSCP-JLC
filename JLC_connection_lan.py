# CSCP_connection
# Used by the CSCP-MIDI application.
# Provides a class/object to Handle IP connection with mixer using socket library
# Runs a thread receiving data checking for valid CSCP messages
# Provides public methods to send messages and to get received messages
# Copyright Peter Walker 2020.
# Feedback - peter.allan.walker@gmail.com

# See Readme.txt for info on how to use this app.
# See Project_Notes.txt for info on the implementation - how the app works.

# TODO - fix jumpy faders - block messages if either end making fader adjsuts?
# drop x out of y fader messages within buffer when lots.
# Use UDP????
# - socket.SOCK_DGRAM  https://realpython.com/python-sockets/
# write a test app/dummy mixer, poss in C++

import socket
import threading
import time

#import CSCP_unpack as unpack
#import CSCP_decode as parse
import CSCP_encode as encode

import JLC_unpack_02 as unpack
import JLC_decode as parse

TIMEOUT = 3  # how long to wait when starting connection and receiving data.
RECEIVE_TIMEOUT = 10


class Connection:
    """
    A CSCP Connection object
    Forms an IP connection
    Runs a thread monitoring the connection,
    periodically attempting reconnect when not connected or connection is lost
    When connected, validates received messages and stores them as CSCP Message objects
    Provides methods to get received messages and to send CSCP Message objects
    """

    # TODO - DROPPING CONNECTION ON LACK OF DATA BECAUSE I'M NOT PINGING WHEN IDLE(?)
    # EITHER ASSUME CONNECTION IS UP, OR PING FOR DATA BACK FROM JLC WHEN IDLE

    def __init__(self, ip_address, tcp_port):

        self.address = ip_address
        self.port = tcp_port
        self.sock = False
        self.status = 'Starting'
        self.messages = []

        # Potentially, there may be residual data at the end of chunk of received data
        # that cannot be parsed but might be the beginning of a message
        # whose remainder is in the next chunk data to be received
        # So will save any such residual data and prepend to the next chunk received
        self.residual_data = False

        # Set up to run in thread
        self.receiver = threading.Thread(target=self._run)
        # I believe the following line causes the thread to stop when the main application stops
        # ... means e.g. control+c will release the terminal
        # (before adding this I had to keep closing terminal each time I wanted to stop the program)
        self.receiver.daemon = True
        self.receiver.start()

    def _connect(self):
        """ Called by _run on initialisation of Connection class """

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(TIMEOUT)
            self.sock.connect((self.address, self.port))
            print('JLC_connection: Socket connection established with address {} on port {}'.format(self.address,
                                                                                                     self.port))

            # Send a message to get some data back
            ping = encode.read_back('read_console_info')
            self.send(ping)
            self.status = "Connected"

        except socket.timeout:
            print('JLC_connection: Failed to create connection with IP address {} on port {}'.format(self.address,
                                                                                                      self.port))
            self.close()
            self.sock = False

    def _run(self):
        """
        Called by init's self.receiver thread
        Make and monitor a connection and listen for incoming CSCP messages
        """
        # if not connected, try to create a socket connection every 5s.

        while not self.sock:
            #print("JLC - NO CONNECTION")
            if not self.status == 'Connection Lost!':
                self.status = 'Not Connected'

            self._connect()
            time.sleep(5)  # Wait before trying to connect again

        # TODO - Check the following if I'm missing messages or getting jittery fader control
        self.sock.settimeout(RECEIVE_TIMEOUT)

        self.pinged = False

        # Listen for incoming messages
        while True:
            try:
                data = self.sock.recv(1024)

                #print(data)
            except socket.timeout:
                data = False

            # print('CSCP_connection run: data received', data, 'pinged', self.pinged)

            if data:
                self.pinged = False
                # Unpack messages from received bytes, checking residual data from previous call
                # to check if a message spanned 2 received chunks

                #messages = False
                messages, self.residual_data = unpack.unpack_data(data, self.residual_data)
                if messages:
                    for msg in messages:
                        self.messages.append(parse.Message(msg))
                        #self.messages.append(msg)

            """
            elif self.pinged:
                # No data received even after mixer being pinged
                self.status = "Connection Lost!"
                print("DEBUG JLC_connect, dropping connection!")
                self.close()
                self._connect()
                self._run()

            else:
                # No data received, send a message to see if the mixer is still there
                # TODO - Check this, I'm not pinging all the time? thought I had set a timeout to trigger this
                self.pinged = True
                # print('CSCP_connection_2_1>run: no messages received for {}s, pinging mixer'.format(RECEIVE_TIMEOUT))
                # TODO - Send a ping that will get a response from JLC!
                ping = encode.read_back('read_console_name')
                self.send(ping)
             """

    def close(self):
        self.sock.close()
        try:
            # TODO - Check this. Pycharm is highlighting it but not similar usage in MIDI_connection
            # ... close is a regular function in midi_connection though, not a class method!
            self.receiver.stop()
        # TODO - What type of exception will threading raise if it can't stop the thread?
        except:
            pass

    # PUBLIC METHODS
    def send(self, msg):
        """
        Public method to send a message to the mixer
        :param msg: CSCP_encode.Message object
        """
        if self.status == "Connected":
            try:
                # TODO - take message object so dont have to pass msg.encoded in main
                # Will need to fix the ping read console info message from encode.
                self.sock.sendall(msg)
            except AttributeError:
                pass  # If failed to create connection, self.sock will == False.
            except socket.timeout:
                pass

    def get_message(self):
        """
        public / called externally
        - removes and returns the oldest message in the buffer
        :return: CSCP Message object
        """
        r = False
        if self.messages:
            r = self.messages[0]
            self.messages = self.messages[1:]
        return r

    def flush(self):
        self.messages = []


if __name__ == '__main__':

    #address = "192.169.1.200"

    address = "192.168.200.114"  # Default address for JLC

    port = 49300 # default port for JLC

    print(20 * '#' + ' JLC_connection ' + 20 * '#')
    connection = Connection(address, port)

    test_message = b'\xb0\x07\x7f\x27\x40'  # Opens fader 1 on JLC
    # decoded = parse.Message(test_message)
    # print("DEBUG test message", decoded)

    ##time.sleep(2)

    while not connection.sock:  # check for socket, while till connected
        pass

    connection.send(test_message)

    time.sleep(2)

    while True:
        if len(connection.messages) > 0:
            print("received messages in buffer:", len(connection.messages))

        msg = connection.get_message()
        if msg:
            print("MESSAGE RECEIVED AND PARSED:", msg)


    #for messg in connection.messages:
    #    print(messg)

    #time.sleep(20)

    # print(connection.messages[-1])

    # for message in connection.messages:
    #    print("Controller received:", message)

    #i = 0

"""
    while True:
        print('\n', i, 'qty:', len(connection.messages), 'residual data', connection.residual_data)
        for message in connection.messages:
            print("Controller received:", message)


        if connection.status == "Connected" and i % 1 == 0:
            #connection.send(test_message)
            msg = encode.Message('fader_move', strip, 744, recipient='mixer')
            print("Controller sending", msg)
            connection.send(msg.encoded)

        i += 1
        strip += 1

        time.sleep(2)


"""
