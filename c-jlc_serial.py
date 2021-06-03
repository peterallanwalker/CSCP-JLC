# jlc panel not appearing as a USB midi device.
# After installing a driver from # https://www.jlcooper.com/_php/downloads.php?op=downloads#anchor-eclipseseries
#  it is now appearing as a COM port when connected via USB.

# use pip install pyserial (not pip install serial - that wil give you a "serial does not have Serial" error)

# Am now getting data from jlc, on COM3
# TODO - check com settings and efficient use for data type
# in particular, readline should be used with cuation (for correct EOL etc)
# try not settings rtscts  (currently, sometimes I'm getting a fader touch message bundled on sa,e line as a fader value message

import serial

"""
with serial.Serial() as ser:
    ser.baudrate = 19200
    ser.port = 'COM3'
    ser.open()
    ser.write(b'hello')
"""


def bin_to_hex(value):
    return hex(int(value, 2))

#ser = serial.Serial('COM3', 38400, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)


# The unit communicates at 31250 bits/second for MIDI and 38400 bits/second for RS-232, RS-422 and USB. The
# data format is 1 start bit, 8 data bits 1 stop bit and no parity.


# THINK I NEED STRUCT TO CONVERT TO BYTES LIKE I DID IN CECP ENCODE

# OPEN SERIAL CONNECTION ON COM3 (ASSUMING JLC USB DRIVER IS INSTALLED"
ser = serial.Serial('COM3', 38400, timeout=0, parity=serial.PARITY_NONE, bytesize=8, stopbits=1, rtscts=1)

# TEST COMMAND, OPENS FADER 1
ser.write(b'\xb0\x07\x7f\x27\x40')

# TRY SETTING BACKLIGHT COLOR
#F0h 15h 26h 04h <00uuunnn> 00h <00rrggbb>on <00rrggbb>off F7h

lcd_header = b'\xf0\x15\x26\x04'
display = b'x\00'
#panelID = b'x\00'
#lcd = b'\x00'
set_color_command = b'\x00'

#on_color = b'\x00\xff\x00\x00'
#off_color = b'\x00\x00\x11\x00'

#on_color = hex(48)
#off_color = hex(48)
#on_color = b'b\00110000'

on_color = b'11'
off_color = b'30'


eom = b'\xf7'

message = lcd_header + display + set_color_command + on_color + off_color + eom
#message = lcd_header + panelID + lcd + set_color_command + on_color + off_color + eom
ser.write(message)
ser.flush()
# ser.write(b'\xf0\x15\x26\x04\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x00\x11\x00\xF7')

# Listen for incoming messages -

while True:
    s = ser.readline()
    if s:
        print(s)
        for d in s:
            #print(bin_to_hex(d))
            print(hex(d), d)

        print('-')



#s = ser.read(100)       # read up to one hundred bytes
                        # or as much is in the buffer
#print(s)

