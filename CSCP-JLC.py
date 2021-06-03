
import CSCP_connection
import JLC_connection_lan

import CSCP_encode
import JLC_encode

# this is working so far, to get messages from JLC,
# is laggy though if moving lots of faders,, optmise
#  first, convert and send to CSCP!


if __name__ == '__main__':

    # Open CSCP connection and start thread receiving incoming CSCP messages
    cscp = CSCP_connection.Connection("192.169.1.200", 12345)
    jlc = JLC_connection_lan.Connection("192.168.200.114", 49300)

    while not jlc.sock:
        print("CSCP-JLC, waiting for JLC connection")



    while True:
        jlc_in = jlc.get_message()
        if jlc_in:
            print(jlc_in)

            cscp_msg = CSCP_encode.Message(jlc_in.operation, jlc_in.strip, jlc_in.value * 4)

            print("CSCP-JLC, JLC msg conv to CSCP: ", cscp_msg)

            cscp.send(cscp_msg.encoded)

        cscp_in = cscp.get_message()
        if cscp_in:
            if cscp_in.operation == "fader_move" and cscp_in.strip in range(7):
            #if cscp_in.operation == "fader_move":
                print("CSCP received, ", cscp_in)
                jlc_message = JLC_encode.Message(cscp_in.operation, cscp_in.strip, cscp_in.value)
                print("CSCP CONV TO JLC", jlc_message)
                jlc.send(jlc_message.encoded)

