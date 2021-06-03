# JLC unpack, based on CSCP_unpack
# provides functions to validate and extract CSCP messaged from serial data bytes
# Used by the CSCP_connection.
# Copyright Peter Walker 2020.
# Feedback - peter.allan.walker@gmail.com

# See Readme.txt for info on how to use this app.
# See Project_Notes.txt for info on the implementation - how the app works.

# TODO - document and refactor

import time

import JLC_utils as utils


def _find_header(data: bytes) -> int:
    """ Checks for JLC strip values, which are used as first byte / "SOH" of control messages.
        Returns index of first SOH if found, -1 if not found.
    :param data: bytes
    :return: int, index of first potential control message header
    """
    for i, byte in enumerate(data):
        if byte in utils.JLC_STRIPS:
            return i
    return -1


def _get_control_type(control_byte: int) -> str:
    if control_byte in utils.JLC_CONTROLS:
        return utils.JLC_CONTROLS[control_byte]
    else:
        return False


def _is_checksum_valid(message, header_byte, byte_count):
    # TODO - make generic checksum creator for building messages and validating (replace the compare below)
    message_checksum = message[header_byte + utils.CSCP_HEADER_LENGTH + byte_count]
    compare_checksum = 0

    # Loop through payload bytes
    for i in range (header_byte + utils.CSCP_HEADER_LENGTH, header_byte + utils.CSCP_HEADER_LENGTH + byte_count):
        compare_checksum += message[i]

    compare_checksum = utils.twoscomp(bin(compare_checksum))

    if message_checksum == int(compare_checksum, 16):
        return True
    else:
        return False


def unpack_data(data, previous_insufficient_data=False):
    """ Takes bytes, (and any residual bytes returned from previous call).
        Extracts and returns valid CSCP messages found within
        also returns any residual data from the end that could be the beginning of a valid message
        (with remainder of message in next bytes to be received - to supply to this function in next call)

    :param data: bytes
    :param previous_insufficient_data: bytes (possible start of message from preceding data)
    :return: bytes, bytes or bool (extracted messages, residual data that may be beginning of message who's remainder
                is due in next received data
    """

    if previous_insufficient_data:
        data = previous_insufficient_data + data  # TODO - test this

    messages = []
    insufficient_data = False

    while len(data) > 0:

        header_byte = _find_header(data)  # First index within data containing a CSCP start of header value (0xF1 / 241)

        if header_byte != -1:  # a potential header byte is within the remaining data
            control_type = _get_control_type(data[header_byte + 1])
            if control_type:
                print(control_type)
                if control_type == "fader_move" and data[header_byte + 3] == 39:  # Valid fader move message

                    print(data[header_byte + 2], data[header_byte + 4])  # TODO, checl for 27 in middle to validate as fader move message
                    messages.append(data[header_byte:header_byte+4])
                    data = data[header_byte + 4:]

                else:
                    data = data[header_byte + 1:]  # strip off the parsed message - TODO - get rest of message!
            else:
                data = data[header_byte:]
        else:
            break  # No more CSCP start of headers found

    #print ('messages extracted:', messages, ' insufficient_data:', insufficient_data)
    return messages, insufficient_data


if __name__ == '__main__':

    # Some data received from the JLC
    test_data = [
                    b"\xb1\x072'@\xb2\x07?'\x00\xb3\x072'\x00",
                    b"\xb1\x07.'\x00\xb2\x07>'\x00\xb3\x071'@\xb1J\x00\xb2\x07='@",
                    b"\xb1\x070'\x00\xb2\x07@'@",
                    b"\xb1\x075'@\xb2\x07E'@\xb3\x074'\x00",
                    b"\xb1\x07<'@\xb2\x07M'\x00\xb3\x07;'@",
                    b"\xb1\x07C'\x00\xb2\x07S'@\xb3\x07D'@",
                    b"\xb1\x07K'\x00\xb2\x07W'\x00\xb3\x07J'@\xb1J\x7f\xb1\x07R'@\xb2\x07['\x00\xb2J\x00\xb3\x07M'\x00",
                    b"\xb1\x07W'@\xb2\x07\\'@\xb3\x07P'\x00",
                    b"\xb1\x07X'\x00\xb2\x07]'\x00",
                    b"\xb1\x07U'@\xb2J\x7f",

                ]


    def test_unpack(test_data):
        print('test data:')
        print('data', test_data, '\n')
        for d in test_data:
            print(d, end=", ")
        print("\n")

        extracted_data = unpack_data(test_data)

        print('messages extracted:')
        for message in extracted_data[0]:
            print(message)

        print('number of messages extracted:', len(extracted_data[0]))

        print('\nresidual data:', extracted_data[1])

    """
    for data in test_data:
        test_unpack(data)
        time.sleep(3)
    """
    test_unpack(test_data[9])

    """
    # test valid message split across two sets of data
    messages, residual = unpack_data(test_data_split[0])
    print(messages, residual)
    messages, residual = unpack_data(test_data_split[1], residual)
    print(messages, residual)
    """