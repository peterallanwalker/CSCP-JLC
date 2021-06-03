
import time

import CSCP_connection
import JLC_connection_lan

import CSCP_encode
import JLC_encode

import CSCP_JLC_settings as config

import JLC_display_03 as display


VERSION = "beta v0.6"
CUSTOMER = "ITN / DB"

# BASED ON V_04 (DITCHED V_05)

# TODO - get mixer label
# STORE CUT/ON STATES
# Get USB working as a config option
# add contact info to terminal
# make ITN specific
# display mixer name and ITN and CAL-JLC on top rows
# maybe refresh display text when a change in labels is identified
# Or maybe detect 3 x display buttons being held down


# This is working so far, have 2-way fader control
# - is a bit laggy if moving around 6 faders at same time though
# - control jitter is not too bad, but there is a little kick back at time

# Check for stability, long term running
# handle JLC connection better - currently drops and reconnect if idle for a time (ping/idle check needs updating from CSCP console readback to a JLC readback
# handle the jitter

"""
class Mixer:
    def __init__(self, strips=8):
        self.strips = []
        
        for s in range(strips):
            self.strips.append(Strip(f))
"""


class Strip:
    """
    Class to store mixer state that can be read from / written to by CSCP or JLC
    Need this as CSCP sends absolute values, e.g. PFL=1, whereas JLC sends button press and release
    events rather than state.

    At the moment, this will just be used for path cut data.

    Fader data does not pass through this class, for that we simply translate and forward straight away.
    for button states, we will read and right from this object class instead.
    """
    def __init__(self, strip, cscp_connection, jlc_connection):
        self.strip = strip
        self.cscp = cscp_connection
        self.jlc = jlc_connection
        self.on = True  # Assuming not cut at startup

    def __str__(self):
        return "CSCP-JLC Strip object, strip: {}, on-state: {}".format(self.strip, self.on)

    def get_on_state(self):
        """
            Call this from JLC to set button leds on/off
            ... Or instead of calling every loop or n loops,
                push it to JLC on change (when set_on_state called)
        :return:
        """
        # TODO - Actually, dont need this, just push message to JLC on change from CSCP
        return self.on

    def set_on_state(self, value):
        """
            THis is intended to be called by the CSCP Mixer, as it holds the true state of the control, and its messages
            implictly set the state as on or off when it changes.

            value, int/bool 1 or True sets path enabled/on, 0 / False sets path cut.
        """
        self.on = value
        # TODO - send button LED=on/off to JLC
        jlc_msg = JLC_encode.Message("cut_toggle", self.strip, self.on)
        #print("CSCP converted TO JLC: ", jlc_msg)
        jlc.send(jlc_msg.encoded)

    def toggle_on_state(self):
        """
            This is intended to be called by the JLC controller, as it just gives messages for button press down and
            release (no state indication)

            THIS FUNCTION IS THE MAIN PURPOSE OF THIS CLASS, AND STORING OF CUT/ON STATE
            SO WE DO NOT HAVE TO QUERY CSCP FOR THE CURRENT STATE WHEN JLC BUTTONS ARE PRESSED
        :return:
        """
        # Update the data model
        self.on = not self.on

        # Update the CSCP mixer
        cscp_msg = CSCP_encode.Message("cut_toggle", settings["Mixer Faders"][jlc_in.strip], self.on)  # TODO - check, self.on == 0/1 or True/False
        #print("JLC converted to CSCP: ", cscp_msg)
        cscp.send(cscp_msg.encoded)

        # TODO also send message back to JLC to set LED state - Same as called by set_on_state... should be part of JLC_encode


def initialise_labels(settings):
    """ Create list for labels,
        defaulting to mixer fader numbers mapped in settings file to JLC faders 1-8
    """
    r = []
    for f in range(8):
        r.append(str(settings["Mixer Faders"][f] + 1))
    return r


def display_test(jlc):
    # Playing with displays...

    # Header for display messages
    lcd_header = b'\xf0\x15\x26\x04'

    # The display being addressed
    #display = b'\x01'  # 0 - 7 are displays 1-8 on first panel.
    displays = (b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07')

    # Display commands
    set_color_command = b'\x00'
    set_mode_command = b'\x01'  # Mode determines number of lines / size of font / chars per line
    set_chars_command = b'\x03'  # Command to set text on the display

    on_color = b'\x30'
    off_color = b'\x30'

    red = b'\x30'
    blue = b'\x03'


    mode_4_lines = b'\x02'

    line_1_text = b'\x01'

    test_text = b'\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'
    # test_text = b'abcdefghij'

    eom = b'\xf7'  # End of message byte

    # message = lcd_header + display + set_color_command + on_color + off_color + eom
    # print("COLOR MESSAGE", message)

    # message = lcd_header + display + set_mode_command + mode_4_lines + eom
    # jlc.send(message)

    # Set display 2 to red
    #message = lcd_header + display + set_color_command + on_color + off_color + eom
    #jlc.send(message)

    # Flash display 3 red and blue.
    #message = lcd_header + displays[2] + set_color_command + blue + red + eom
    #jlc.send(message)

    for disp in range(8):
        message = lcd_header + displays[disp] + set_color_command + blue + blue + eom
        jlc.send(message)

    message = lcd_header + displays[1] + set_chars_command + b'\x00' + b'\x26\x26\x26\x26\x26\x26\x26\x26\x26\x26' + eom
    jlc.send(message)

    for disp in range(8):
        time.sleep(2)
        print("TEST TEXT, display", disp)
        display.set_text(jlc, disp, 3, "xxx " + str(disp))


def display_test_2(jlc):

    for d in range(8):
        print("display test, setting display", d)
        display.set_color(jlc, d, "red")
        #time.sleep(1)


def set_labels(jlc, labels):
    """ Write labels to JLC displays
        writing text to JLC displays is slow and unreliable
        Doing it twice like this with small delay seems to get them all written
        TODO - Figure out / debug this more
    """

    i = 0
    while i < 8:
        display.set_text(jlc, i, 0, labels[i])
        i += 1
        time.sleep(0.1)
    i = 7
    while i >= 0:
        display.set_text(jlc, i, 0, labels[i])
        i -= 1
        time.sleep(0.1)


def displays_all_blue(jlc):
    for d in range(8):
        display.set_color(jlc, d, "blue")


def display_text_test(jlc):
    for d in range(8):
        display.set_text(jlc, d, 1, "test " + str(d))
        time.sleep(5)


def fader_test_2(jlc):

    incrementing = [True, True, True, True, True, True, True, True]
    values = [0, 0, 0, 0, 0, 0, 0, 0]

    while True:
        for fader in range(8):
            message = JLC_encode.Message("fader_move", fader, values[fader])
            jlc.send(message.encoded)
            if incrementing[fader]:
                values[fader] += 10
                if values[fader] >= 1000:
                    incrementing[fader] = False
            else:
                values[fader] -= 10
                if values[fader] <= 0:
                    incrementing[fader] = True


def fader_test(jlc):

    incrementing = True
    value = 0

    for fader in range(8):
        display.set_text(jlc, fader, 0, "hello " + str(fader + 1))
        #time.sleep(0.1)
        #display.set_color(jlc, fader, "red")
        #display.set_text(jlc, fader, 0, str(fader + 1))

        #message = JLC_encode.Message("fader_move", fader, 1000)
        #jlc.send(message.encoded)
        #time.sleep(0.1)

    for fader in range(8):
        message = JLC_encode.Message("fader_move", fader, 0)
        jlc.send(message.encoded)
        #display.set_color(jlc, fader, "blue")
        time.sleep(0.1)


def wait_for_cscp(cscp, labels):

    # Wait for CSCP connection and get labels
    #while not cscp.status == "Connected":
    #    pass

    # wait a bit to get display/info from mixer # TODO - tweak/improve on this
    time.sleep(1)
    # TODO - ASK FOR LABELS INSTEAD OF WAITING!

    labels_found = 0

    tries = 0
    timeout = 1000000
    print("Waiting for labels from mixer...")
    while labels_found < 8 and tries < timeout:
        cscp_in = cscp.get_message()
        #print(cscp_in)
        #print("waiting for labels...", tries)
        if cscp_in:
            #print(cscp_in)
            if cscp_in.operation == "read_fader_label" and cscp_in.strip in settings["Mixer Faders"]:

                print("CSCP-JLC - fader label received from CSCP, strip: {}, label: {}".format(cscp_in.strip,
                                                                                               cscp_in.value))
                """
                if len(cscp_in.value) > 10:
                    cscp_in.value = cscp_in.value[:10]  # truncate to 1st 10 chars
                    # print("LABEL TRUNCATED TO 10 CHARS", cscp_in.value, len(cscp_in.value))

                elif len(cscp_in.value) < 10:
                    cscp_in.value = cscp_in.value.ljust(10)
                    # print("LABEL PADDED TO 10 CHARS", cscp_in.value, len(cscp_in.value))
                """

                labels_found += 1

                # Convert CSCP fader to 1-8 for JLC
                labels[settings["Mixer Faders"].index(cscp_in.strip)] = cscp_in.value
        #print("waiting for labels from cscp....")
        tries += 1
    return labels


def get_mixer_name(cscp):
    # Takes CSCP connection object
    # returns mixer name if found
    msg = CSCP_encode.read_back('read_console_name')
    cscp.send(msg)
    # TODO - TUNE THIS

    i = 0
    print("Waiting for CSCP mixer's name...")
    while i < 100000:
        #print("get_mixer_name, receive", i)
        cscp_in = cscp.get_message()
        #print("Waiting for console name...", cscp_in)
        if cscp_in and cscp_in.operation == "read_console_name":
            #print("get_mixer_nmae, found:", cscp_in.value)
            return cscp_in.value
        i += 1
    return ""


if __name__ == '__main__':

    # Formatted title/heading
    print("\n", 30 * "=", "\n", 4 * " ", "CAL-JLC\n", 4 * " ", "version: ", VERSION, "\n", 4 * " ", "Built for", CUSTOMER, "\n", 30 * "-", "\n")
    # TODO - ADD CONTACT ADDRESS

    # Get connection settings
    settings = config.get_settings()

    # Save connection settings for next start up
    config.save_settings(settings)  # TODO, should really wait till connections are established before saving

    # Initialise default fader labels
    labels = initialise_labels(settings)
    #print("LABELS: ", labels)

    # Open connections
    cscp = CSCP_connection.Connection(settings["Mixer IP Address"], settings["Mixer CSCP Port"])
    jlc = JLC_connection_lan.Connection(settings["JLC IP Address"], settings["JLC Port"])

    # Wait a while for CSCP and get labels if up before starting - TODO - TAKES A WHILE, REQUEST LABELS RATHER THAN WAITING,
    labels = wait_for_cscp(cscp, labels) # TODO - UNCOMMENT FOR PRODUCTION, FIND BETTER TIMEOUT FOR WAITING

    #print("LABELS: ", labels)  # WHT IS THIS PRINTING THE DEFAULT INITIALISED LABELS?

    #cscp.flush()
    mixer_name = get_mixer_name(cscp)  # TODO, this is slow as well, and this one requests the data ratehr than just waiting?

    # Set up displays
    displays = []
    heading = ""

    # Headings to display based on which display it is
    for f in range(8):
        if f == 0:
            heading = "CAL-JLC"
        elif f == 1:
            heading = CUSTOMER
        elif f == 2:
            heading = mixer_name
        else:
            heading = ""

        # Create display objects
        displays.append(display.Display(f, label=labels[f], header=heading))

        # Tell JLC to set the display text and color
        displays[f].write_text(jlc)
        displays[f].write_color(jlc)
        #print("CSCP_JLC_06 - Display:", displays[f])

    # Setup data for storing button states
    # TODO - displays shoudl realy be part of strips which should be part of a mixer parent object
    strips = []
    for f in range(8):
        strips.append(Strip(f, cscp, jlc))

    # Wait for JLC panel connection - Comment out for debug/test without JLC panel
    #while not jlc.status == "Connected":
    #    pass
        # TODO - readback fw ver.. sock may be up before unit accepts commands

    # Set unit to respond when display writes are completed
    #msg = b'\xf0\x15\x26\x04\x00\x07\x01\xf7'
    #jlc.send(msg)
    #time.sleep(2)

    #displays_all_blue(jlc)

    # not all labels being set, my need to slow down the writing?
    """
    for f in range(len(labels)):
        display.set_text(jlc, f, 0, labels[f])
        # Wait for unit to respond with display write complete


        time.sleep(1)
        #display.set_color(jlc, f, "red")
        #time.sleep(1)
        print("updating displays...")
        # TODO, ADD DELAY AND/OR SET COLOR (SEEMS TO FLUSH)
        # READBACK WHEN READY!
    """

    #set_labels(jlc, labels)

    #displays_all_blue(jlc)

    #displays_all_blue(jlc)

    #display_text_test(jlc)

    #display.set_text(jlc, 0, 0, "CAL-JLC")



    #time.sleep(5)
    #msg = JLC_encode.Message("fader_move", 0, 744)
    #print(msg)
    #jlc.send(msg.encoded)


    #fader_test(jlc)
    #fader_test_2(jlc)

    #while not cscp.status == "Connected":
    #    pass

    cscp.flush()
    jlc.flush()

    #  Main program loop
    while True:

        jlc_in = jlc.get_message()
        if jlc_in:
            #print("JLC message received:", jlc_in)
            #  Convert JLC to CSCP

            # TODO - IMPROVE THIS
            if jlc_in.operation == "fader_move":
                cscp_msg = CSCP_encode.Message(jlc_in.operation, settings["Mixer Faders"][jlc_in.strip], jlc_in.value * 4)
                #print("CSCP-JLC JLC FADER MSG RECEIVED")
                #print("JLC converted to CSCP: ", cscp_msg)
                cscp.send(cscp_msg.encoded)

            elif jlc_in.operation == "cut_toggle" and jlc_in.value:
                # JLC Cut button down event
                strips[jlc_in.strip].toggle_on_state()
                #print("CSCP-JLC JLC CUT BUTTON DOWN RECEIVED")

            else:
                #print("JLC MSG TYPE ", jlc_in.operation)
                pass

            #print("JLC converted to CSCP: ", cscp_msg)
            #
            #print("messages in JLC receive buffer: ", len(jlc.messages))

            # Precautionary hack to prevent lag or overflow # TODO - check/test/improve/remove
            if len(jlc.messages) > 5000:
                print("FLUSHING JLC")
                jlc.flush()

        cscp_in = cscp.get_message()
        if cscp_in:
            #print(cscp_in)
            if settings["Two-Way Fader Control"] and cscp_in.operation == "fader_move" and cscp_in.strip in settings["Mixer Faders"]:
                #print("CSCP message received: ", cscp_in)
                # TODO - CHECK THIS, NOW LOOKING UP FADER STRIP MAPPING
                jlc_msg = JLC_encode.Message(cscp_in.operation, settings["Mixer Faders"].index(cscp_in.strip), cscp_in.value)
                #print("CSCP converted TO JLC: ", jlc_msg)
                jlc.send(jlc_msg.encoded)
                #print("messages in CSCP receive buffer: ", len(cscp.messages))

            elif cscp_in.strip in settings["Mixer Faders"] and cscp_in.operation == "cut_toggle":
                #print("CSCP-JLC, cut message from CSCP", cscp_in)
                strips[cscp_in.strip].set_on_state(cscp_in.value)

                #for f in strips:
                #    print(f)

            # Precautionary hack to prevent lag or overflow # TODO - check/test/improve/remove
            if len(cscp.messages) > 5000:
                print("FLUSHING CSCP")
                cscp.flush()


