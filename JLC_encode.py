
# take params from a CSCP message object and create one to send to JLC

# TODO !!!!! got 4 classes doing the same thing, need to make one with different interfaces

import JLC_utils as utils


class Message:
    """ THIS JUST HANDLES FADER MESSAGES AT THE MO """
    def __init__(self, operation, strip, value):

        self.operation = utils.CSCP_CONTROLS[operation]

        self.strip = utils.JLC_STRIPS[strip]

        if operation == "fader_move":

            self.value = int(value / 4)  # CSCP fader range = 0-1024, JLC = 0-255 (/4)

            if self.value > 255:
                self.value = 255.

        elif operation == "cut_toggle":
            if value:
                self.value = 127
            else:
                self.value = 0

        self.encoded = False
        self.encoded = self._encode()

    def __str__(self):
        return "JLC Message: Strip - {}, Operation - {}, Value - {}, Encoded - {}".format(self.strip, self.operation, self.value, self.encoded)

    def _encode(self):
        if self.operation == utils.CSCP_CONTROLS["fader_move"]:
            fader_value_byte1, fader_value_byte2 = fader_to_jlc_bytes(self.value)
            #print("JLC fader vals", fader_value_byte1, fader_value_byte2)
            message = [self.strip, self.operation, fader_value_byte1, 39, fader_value_byte2]

        elif self.operation == utils.CSCP_CONTROLS["cut_toggle"]:
            message = [self.strip, self.operation, self.value]

        #print(message)
        message = bytes(message)
        return message


def fader_to_jlc_bytes(value):

    # take int in range 0 - 1024,
    # convert to two bytes -
    # byte one is /2 (bytesihft right?)
    # byte two bit 6 or 7 is LSB
    # .. cant just do that... can't -1 if dont know if 1 added in first place

    # work out if 1 was added  - is LSB 1 ?
    # ... i.e. is odd or even? %2 == 0?

    if value % 2 != 0: # if odd
        value -= 1
        #byte2 = hex(64)  # but 6 for LSB
        byte2 = 64  # but 6 for LSB
    else:
        byte2 = 0x0

    # TODO check this, should I use math.floor??
    byte1 = int(value / 2)  # bit shifts right the binary equivalent

    return byte1, byte2










# https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
# mydict = {'george': 16, 'amber': 19}
# print(list(mydict.keys())[list(mydict.values()).index(16)])  # Prints george