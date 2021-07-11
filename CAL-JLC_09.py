# CAL-JLC: two-way protocol translator
# provides comms between audio mixer supporting the CSCP protocol (Calrec mixers)
# and JL Cooper fader panels

import time
import sys
import pyperclip  # for copying host uid to clipboard to help users obtain license

import CSCP_connection
import JLC_connection_lan

import CSCP_encode
import JLC_encode

import CSCP_JLC_settings as config

import JLC_display_03 as display

import licensing
import terminal_formatter
import web_info

# added licensing

TITLE = "CAL-JLC Mixer Control"
VERSION = "1.0"
EVAL_PERIOD = 10 * 60  # Number of seconds program will run for in unlicensed evaluation mode


# TODO maybe...
# Get USB working as a config option
# Check for stability, long term running
# handle JLC connection better - currently drops and reconnect if idle for a time (ping/idle check needs updating from CSCP console readback to a JLC readback
# handle the fader jitter (JLC OK AS LONG AS TOUCH MAINTAINED, ELSE CAN GET SNAP BACK
# DONT ALLOW CSCP FADER WRITES FOR N TIME AFTER JLC FADER WRITES?

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
        # print("CSCP converted TO JLC: ", jlc_msg)
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
        # print("JLC converted to CSCP: ", cscp_msg)
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


def wait_for_cscp(cscp, labels):

    # Wait for CSCP connection and get labels
    # while not cscp.status == "Connected":
    #    pass

    # wait a bit to get display/info from mixer # TODO - tweak/improve on this
    time.sleep(1)
    # TODO - ASK FOR LABELS INSTEAD OF WAITING!

    labels_found = 0

    tries = 0

    # Set max number of attempts so we're not waiting forever,
    # Note, if debug printing each try, the print statement slows this down a LOT
    # ... when the print is commented out, need to increase the timeout value
    # timeout = 1000000  # Appropriate value when printing each pass through the loop
    timeout = 100000000 # increased number of tries for when not printing - TODO, make this more sophisticated

    print("Waiting for labels from mixer...")
    while labels_found < 8 and tries < timeout:
        cscp_in = cscp.get_message()

        # print(cscp_in)
        # print("waiting for labels...", tries)
        if cscp_in:
            # print(cscp_in)
            if cscp_in.operation == "read_fader_label" and cscp_in.strip in settings["Mixer Faders"]:

                # print("CSCP-JLC - fader label received from CSCP, strip: {}, label: {}".format(cscp_in.strip, cscp_in.value))
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
        # print("waiting for labels from cscp....")
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
    while i < 1000000:
        # print("get_mixer_name, receive", i)
        cscp_in = cscp.get_message()
        # print("Waiting for console name...", cscp_in)
        if cscp_in and cscp_in.operation == "read_console_name":
            # print("get_mixer_nmae, found:", cscp_in.value)
            return cscp_in.value
        i += 1
    return ""


if __name__ == '__main__':

    # CHECK FOR LICENSE FILES AND VALIDATE AGAINST THE HOST MACHINE'S UID
    valid = licensing.validate_license(licensing.KEY)

    if not valid:
        # sys.exit()  # Quit the program
        customer_name = "EVALUATION"
        system_name = ""
        host_uid = licensing.get_host_uid()
        pyperclip.copy(host_uid)  # copy host uid to clipboard
        license_help = ("No license found",
                        "** RUNNING IN SHORT-TERM EVALUATION MODE **",
                        "Your product key: {} has been copied to the clipboard".format(host_uid),
                        "Paste and email to {} to obtain a license and unlock full access".format(web_info.CONTACT),
                        "Go to {} for more information.".format(web_info.WEB),
                        "Evaluation mode starting in 10s...")

        terminal_formatter.print_heading(TITLE, VERSION, license_help)
        time.sleep(10)
        start_time = time.time()  # Used to time how long application has been running (for evaluation mode)

    else:
        customer_name = valid[0]
        system_name = valid[1]
        welcome_text = ("Licensed for {} {}".format(customer_name, system_name),
                        web_info.WEB,
                        web_info.CONTACT)

        terminal_formatter.print_heading(TITLE, VERSION, welcome_text)
        time.sleep(5)  # Pause to allow users to read title info

    # Get connection settings
    settings = config.get_settings()

    # Save connection settings for next start up
    config.save_settings(settings)  # TODO, should really wait till connections are established before saving

    # Initialise default fader labels
    labels = initialise_labels(settings)

    # Open connections
    cscp = CSCP_connection.Connection(settings["Mixer IP Address"], settings["Mixer CSCP Port"])
    jlc = JLC_connection_lan.Connection(settings["JLC IP Address"], settings["JLC Port"])

    # Wait a while for CSCP and get labels if up before starting
    # - TODO - TAKES A WHILE, REQUEST LABELS RATHER THAN WAITING,
    labels = wait_for_cscp(cscp, labels)

    # print("LABELS: ", labels)  # WHT IS THIS PRINTING THE DEFAULT INITIALISED LABELS?
    # cscp.flush()

    mixer_name = get_mixer_name \
        (cscp)  # TODO, this is slow as well, and this one requests the data ratehr than just waiting?

    print("Configuring JLC displays...")
    # Set up displays
    displays = []
    heading = ""

    # Headings to display based on which display it is
    for f in range(8):
        if f == 0:
            heading = "CAL-JLC"
        elif f == 1:
            heading = VERSION
        elif f == 2:
            heading = customer_name
        elif f == 3:
            heading = system_name
        elif f == 4:
            heading = mixer_name
        else:
            heading = ""

        # Create display objects
        displays.append(display.Display(f, label=labels[f], header=heading))

        # Tell JLC to set the display text and color
        displays[f].write_text(jlc)
        displays[f].write_color(jlc)
        # print("CSCP_JLC_06 - Display:", displays[f])

    # Setup data for storing button states
    # TODO - displays should really be part of strips which should be part of a mixer parent object
    strips = []
    for f in range(8):
        strips.append(Strip(f, cscp, jlc))

    # Wait for JLC panel connection - Comment out for debug/test without JLC panel
    # while not jlc.status == "Connected":
    #    print("waiting for JLC connection...")
    # TODO - readback fw ver.. sock may be up before unit accepts commands

    cscp.flush()
    jlc.flush()
    print("Running")

    # MAIN PROGRAM LOOP
    while True:

        # When running without a valid license, quit after evaluation time period
        if not valid:
            #print("timer", time.time() - start_time)
            if time.time() - start_time >= EVAL_PERIOD:
                terminal_formatter.print_footer("EVALUATION TIME IS UP",
                                                "Your product key {} has been copied to the clipboard".format(host_uid),
                                                "Paste and email to {} to obtain a license for full access to this software".format(web_info.CONTACT),
                                                "Goto {} for more information".format(web_info.WEB))
                time.sleep(30 * 60)  # Sleep for 30 mins to give chance for someone to read the message before the window closes
                # TODO - stop connection threads / prevent messaging to the above message it the last thing displayed
                sys.exit()  # When running from an exe, this causes window to close so you can't see the message


        jlc_in = jlc.get_message()
        if jlc_in:
            # print("JLC message received:", jlc_in)
            #  Convert JLC to CSCP

            # TODO - IMPROVE THIS
            if jlc_in.operation == "fader_move":
                cscp_msg = CSCP_encode.Message(jlc_in.operation, settings["Mixer Faders"][jlc_in.strip], jlc_in.value * 4)
                # print("CSCP-JLC JLC FADER MSG RECEIVED")
                # print("JLC converted to CSCP: ", cscp_msg)
                cscp.send(cscp_msg.encoded)

            elif jlc_in.operation == "cut_toggle" and jlc_in.value:
                # JLC Cut button down event
                strips[jlc_in.strip].toggle_on_state()
                # print("CSCP-JLC JLC CUT BUTTON DOWN RECEIVED")

            else:
                # print("JLC MSG TYPE ", jlc_in.operation)
                pass

            # print("JLC converted to CSCP: ", cscp_msg)
            #
            # print("messages in JLC receive buffer: ", len(jlc.messages))

            # Precautionary hack to prevent lag or overflow # TODO - check/test/improve/remove
            if len(jlc.messages) > 5000:
                print("FLUSHING JLC")
                jlc.flush()

        cscp_in = cscp.get_message()
        if cscp_in:
            # print(cscp_in)
            if settings["Two-Way Fader Control"] and cscp_in.operation == "fader_move" and cscp_in.strip in settings["Mixer Faders"]:
                # print("CSCP message received: ", cscp_in)
                # TODO - CHECK THIS, NOW LOOKING UP FADER STRIP MAPPING
                jlc_msg = JLC_encode.Message(cscp_in.operation, settings["Mixer Faders"].index(cscp_in.strip), cscp_in.value)
                # print("CSCP converted TO JLC: ", jlc_msg)
                jlc.send(jlc_msg.encoded)
                # print("messages in CSCP receive buffer: ", len(cscp.messages))

            elif cscp_in.strip in settings["Mixer Faders"] and cscp_in.operation == "cut_toggle":
                # print("CSCP-JLC, cut message from CSCP", cscp_in)
                strips[cscp_in.strip].set_on_state(cscp_in.value)

                # for f in strips:
                #    print(f)

            # Precautionary hack to prevent lag or overflow # TODO - check/test/improve/remove
            if len(cscp.messages) > 5000:
                print("FLUSHING CSCP")
                cscp.flush()

