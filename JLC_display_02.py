# Functions for encoding and sending displau messages to the JLC

TITLE = "CAL-JLC".center(10)
CUSTOMER = "ITN".center(10)


header = b'\xf0\x15\x26\x04'

strips = (b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07')

set_color_command = b'\x00'

set_text_command = b'\x03'

display_feedback_command = b'\x00\x07'

colors = {"off": b'\x00', "red": b'\x30', "blue": b'\x03', "light-blue": b'\x0f'}

display_rows = {b'\x00', b'\x01', b'\x02', b'\x03'}

eom = b'\xf7'  # End of message byte


class Display:
    """
        JLC panel display
    """

    def __init__(self, strip, label):
        self.mode = False  # TODO
        self.strip = strip
        self.text = 40 * " "

    def write_display_text(self, connection):
        """
        Write text to a display on the JLC panel
        Assumes display is set to 4 x 10 character mode

        :param connection: a JLC_connection.Connection() instance.
        :param strip: int, 1-8, JLC fader number.
        :param text: list of 4 strings, one per row on the display
        :return:

        # TODO : this assumes display is in 4 x 10 character mode,
            use len(text) and set the mode of the display if needed
        """
        row_1_text = text[:10].center(10)
        row_2_text = text[11:20].center(10)

        # display_string needs to be a single string of exactly the number of chars to fill all lines for the mode the
        # display is in.
        display_string = ""
        for i in range(len(text)):
            display_string += text[i][:10].center(10)

        message = header + strips[strip] + set_text_command + display_rows[0] + bytes(text, 'utf-8')
        connection.send(message)


def set_color(connection, strip, color):
    """

    :param connection: JLC connection object to send the command
    :param strip: int 0 - 7
    :param color: string from colors dict,
                    or int in range 0-63, representing 7 bit RGB rrggbb
    :return:
    """
    if type(color) == str:
        color = colors[color]

    elif type(color) == int:
        print(color)
        color = bytes([color])
        print("COlor", color)

    #message = header + strips[strip] + set_color_command + colors[color] + colors[color] + eom
    message = header + strips[strip] + set_color_command + color + color + eom
    connection.send(message)


def set_text(connection, strip, row, text):
    # ASSUMES DISPLAY IS SET TO 4 LINE 10 CHAR MODE
    #print("Set_text", strip, strips[strip])
    row = b'\x03'  # 4th row
    #row = bytes(row)
    #print("DISPLAY ROW", row)
    #message = header + strips[strip] + set_text_command + row + bytes(text)
    message = header + strips[strip] + set_text_command + row + bytes(text, 'utf-8')
    connection.send(message)


def set_display_text(display, strip):
    """
    """
    label_row_1 = b'\x02'  # 3rd row of the display
    label_row_2 = b'\x03'  # 4th row of the display

    # Truncate to max of 20 chars, split into two strings padded and centered to 10 chars
    # Note, the slicing works even if string < indexes used for slice
    row_1_text = text[:10].center(10)
    row_2_text = text[11:20].center(10)


def write_display_text(connection, strip, text):
    """
    Write text to a display on the JLC panel
    Assumes display is set to 4 x 10 character mode

    :param connection: a JLC_connection.Connection() instance.
    :param strip: int, 1-8, JLC fader number.
    :param text: list of 4 strings, one per row on the display
    :return:

    # TODO : this assumes display is in 4 x 10 character mode,
        use len(text) and set the mode of the display if needed
    """
    row_1_text = text[:10].center(10)
    row_2_text = text[11:20].center(10)

    # display_string needs to be a single string of exactly the number of chars to fill all lines for the mode the
    # display is in.
    display_string = ""
    for i in range(len(text)):
        display_string += text[i][:10].center(10)

    message = header + strips[strip] + set_text_command + display_rows[0] + bytes(text, 'utf-8')
    connection.send(message)


if __name__ == '__main__':

    import JLC_connection_lan
    import time

    jlc = JLC_connection_lan.Connection("192.168.200.114", 49300)

    count = 0
    while not jlc.status == "Connected":
        print("JLC_display_02, waiting for connection", count)
        count += 1

    color = 0
    while color < 64:
        for strip in range(8):
            print("Strip: {}, Color: {}".format(strip, color))
            set_color(jlc, strip, color)
            color += 1
            time.sleep(0.1)





