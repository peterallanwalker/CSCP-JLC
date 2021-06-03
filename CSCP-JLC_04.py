
import time

import CSCP_connection
import JLC_connection_lan

import CSCP_encode
import JLC_encode

import CSCP_JLC_settings as config

import JLC_display as display


VERSION = "beta v0.4"

# This is working so far, have 2-way fader control
# - is a bit laggy if moving around 6 faders at same time though
# - control jitter is not too bad, but there is a little kick back at time

# Check for stability, long term running
# handle JLC connection better - currently drops and reconnect if idle for a time (ping/idle check needs updating from CSCP console readback to a JLC readback
# handle the jitter


def initialise_labels(settings):
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
    # DISPLAYS DONT TAKE, SETTING THEM TWICE LIKE THIS SEEMS TO BE BEST FOR NOW
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


def wait_for_cscp():

    # Wait for CSCP connection
    while not cscp.status == "Connected":
        pass

    # wait a bit to get display/info from mixer # TODO - tweak/improve on this
    #time.sleep(2)
    # TODO - ASK FOR LABELS INSTEAD OF WAITING
    print("Waiting for labels from mixer")
    labels_found = 0
    while labels_found < 8:
        cscp_in = cscp.get_message()
        if cscp_in:
            if cscp_in.operation == "read_fader_label" and cscp_in.strip in settings["Mixer Faders"]:

                print("CSCP-JLC - fader label received from CSCP, strip: {}, label: {}".format(cscp_in.strip,
                                                                                               cscp_in.value))

                if len(cscp_in.value) > 10:
                    cscp_in.value = cscp_in.value[:10]  # truncate to 1st 10 chars
                    # print("LABEL TRUNCATED TO 10 CHARS", cscp_in.value, len(cscp_in.value))

                elif len(cscp_in.value) < 10:
                    cscp_in.value = cscp_in.value.ljust(10)
                    # print("LABEL PADDED TO 10 CHARS", cscp_in.value, len(cscp_in.value))

                labels_found += 1
                labels[settings["Mixer Faders"].index(cscp_in.strip)] = cscp_in.value


if __name__ == '__main__':

    # Formatted title/heading
    print("\n", 30 * "=", "\n", 4 * " ", "CAL-JLC\n", 4 * " ", "version:", VERSION, "\n", 30 * "-", "\n")

    # Get connection settings
    settings = config.get_settings()

    # Save connection settings for next start up
    config.save_settings(settings)  # TODO, should really wait till connections are established before saving

    # Fader labels
    labels = initialise_labels(settings)
    print("LABELS: ", labels)

    # Open connections
    cscp = CSCP_connection.Connection(settings["Mixer IP Address"], settings["Mixer CSCP Port"])
    jlc = JLC_connection_lan.Connection(settings["JLC IP Address"], settings["JLC Port"])

    # *****************************
    # *** COMMENT OUT FOR DEBUG ***
    # *****************************
    # Wait for CSCP and get labels before starting
    wait_for_cscp()

    print("LABELS: ", labels)



    # Wait for JLC panel connection - Comment out for debug/test without JLC panel
    while not jlc.status == "Connected":
        pass
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

    set_labels(jlc, labels)

    displays_all_blue(jlc)

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
            cscp_msg = CSCP_encode.Message(jlc_in.operation, settings["Mixer Faders"][jlc_in.strip], jlc_in.value * 4)
            #print("JLC converted to CSCP: ", cscp_msg)
            cscp.send(cscp_msg.encoded)
            #print("messages in JLC receive buffer: ", len(jlc.messages))

            # Precautionary hack to prevent lag or overflow # TODO - check/test/improve/remove
            if len(jlc.messages) > 5000:
                jlc.flush()

        cscp_in = cscp.get_message()
        if cscp_in and settings["Two-Way Fader Control"]:
            if cscp_in.operation == "fader_move" and cscp_in.strip in settings["Mixer Faders"]:
                #print("CSCP message received: ", cscp_in)
                # TODO - CHECK THIS, NOW LOOKING UP FADER STRIP MAPPING
                jlc_msg = JLC_encode.Message(cscp_in.operation, settings["Mixer Faders"].index(cscp_in.strip), cscp_in.value)
                #print("CSCP converted TO JLC: ", jlc_msg)
                jlc.send(jlc_msg.encoded)
                #print("messages in CSCP receive buffer: ", len(cscp.messages))

                # Precautionary hack to prevent lag or overflow # TODO - check/test/improve/remove
                if len(cscp.messages) > 5000:
                    print("FLUSHING CSCP")
                    cscp.flush()

        elif not settings["Two-Way Fader Control"]:
            cscp.flush()

