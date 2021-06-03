# Part of Calrec CSCP <--> JL Cooper translator app.
# Peter Walker, May 2021
#
# Connection manager for comms with JL Cooper Eclipse fader panels
# Uses a serial connection over USB
#
# Requires a driver to be installed from https://www.jlcooper.com/_php/downloads.php?op=downloads#anchor-eclipseseries
# Tested with 'Windows Drivers for JLCooper USB Controllers', version 2.12.28, Jun 1st, 2020.
# When connected via USB, this driver makes the JLC appear as a serial COM port in Windows.

# Using pyserial for serial comms.
# use pip install pyserial (not pip install serial - that wil give you a "serial does not have Serial" error)

# On my machine, is coming up as COM3
# TODO - enumerate available COM ports / Allow user selection of COM port

# TODO - base this on CSCP Connection
# - run a thread receiving messages from JLC
# - store received messages
# - provide a method to get received messages
# - provide a method to send messages to JLC
# - Store messages in CSCP format (strip number, fader values etc as per CSCP)
# - Have another file run as a manager, setup both connections and manage which can write when
# - translate CSCP-JLC

# TODO - check https://realpython.com/async-io-python/ alternative to threads

# THIS IS RUNNING SLOW, MIGHT BE BETTER WITHOUT THE PRINT STATEMENTS, BUT SAME CODE NOT RUNNING IN A THREAD
# RUNS IN REALISH TIME, IN A THREAD IT GETS LAGGY.
# ... try ethernet :(

import serial  # pyserial - https://pyserial.readthedocs.io/en/latest/shortintro.html
import threading  # to run connection in background, non-blocking


class Connection:
    # Connection manager for JLCooper panel via USB serial COM port.
    def __init__(self, port):

        self.port = port
        self.connection = False

        self.connection = serial.Serial(self.port, 38400, timeout=0, parity=serial.PARITY_NONE, bytesize=8, stopbits=1,
                                        rtscts=0, dsrdtr=0, xonxoff=0)

        self.messages = []

        self.receiver = threading.Thread(target=self._run)
        self.receiver.daemon = True
        self.receiver.start()

    def _run(self):
        """
        Start serial connection and listen for messages
        """
        # OPEN SERIAL CONNECTION ON COM3 (ASSUMING JLC USB DRIVER IS INSTALLED, SEE NOTES ABOVE)
        #self.connection = serial.Serial(self.port, 38400, timeout=0, parity=serial.PARITY_NONE, bytesize=8, stopbits=1, rtscts=0, dsrdtr=0, xonxoff=0)
        #self.connection = serial.Serial(self.port, 38400, timeout=0, parity=serial.PARITY_NONE, bytesize=8, stopbits=1)

        i = 0
        while True:
            print(i)
            i += 1
            try:
                s = self.connection.readline()
                #self.connection.flush()
            except:
                pass

            if s:
                print(s)
                #print("---\n", s)
                #for d in s:
                #    print(hex(d), "/ ", d)
                #print("---")


            """
            s = self.connection.read() # read one byte
            if s:
                print(s)
            """

    # The following are intended to be externally accessed/public methods
    def get_message(self):
        """
        Returns and removes first message from self.messages
        :return:
        """
        r = False
        if self.messages:
            r = self.messages[0]
            self.messages = self.messages[1:]
        return r

    def send_message(self, msg):
        # print("DEBUG CSCP SEND", msg)
        try:
            self.connection.write(msg)
        except AttributeError:  # if connection is false
            pass


if __name__ == '__main__':
    print(20*"#", "\nJLCooper USB Connection Manager")
    serial_port = "COM3"

    jlc_conn = Connection(serial_port)
    i = 1
    while True:
        if i % 10000000 == 0:
            print(i)
            jlc_conn.send_message(b'\xb0\x07\x7f\x27\x40')
        #print(i)
        i += 1

    #jlc_conn.send_message(msg)







