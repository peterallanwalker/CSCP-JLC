# Parse JLC messages, as extracted by JLC_unpack

import JLC_utils as utils


class Message:

    def __init__(self, message_bytes):
        #print("Decode, bytes:", message_bytes)
        self.strip = utils.JLC_STRIPS.index(message_bytes[0])
        self.operation = utils.JLC_CONTROLS[message_bytes[1]]

        # TODO, validate fader moves with 39 between two values, either here or in unpack
        if self.operation == "fader_move":
            self.value = get_fader_value(message_bytes[2], message_bytes[4])

        elif self.operation == "cut_toggle" and message_bytes[2] != 127:
            #print("JLC_decode, Cut released!!!!")
            self.value = 0

        elif self.operation == "cut_toggle" and message_bytes[2] == 127:  # JLC button down event
            self.value = 1
            #print("JLC_decode, Cut DOWN!!!!")
        """
        elif self.operation == "toggle_cut" and not message_bytes[2] == 127:  # JLC button release event == 0, 
            self.value = 0
        """

    def __str__(self):
        return "JLC Message, Strip: {}, Operation: {}, Value: {}".format(self.strip, self.operation, self.value)


def get_fader_value(byte1, byte2):

    #print("JLC decode, fader val byte 1", byte1, "byte2", byte2)

    fader_value = byte1 * 2  # Equivalent of bit-shift left by one

    if byte2:
        # Byte2 contains the fader val LSB on bit 6
        # SO, assuming we only ever recieve 64 or 0 on this byte...
        fader_value += 1

    return fader_value


if __name__ == '__main__':

    test_data = b"\xb1\x072'@"
    test = Message(test_data)
    print(test)
