# Functions for encoding and sending displau messages to the JLC

header = b'\xf0\x15\x26\x04'

strips = (b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07')

set_color_command = b'\x00'

set_text_command = b'\x03'

colors = {"off": b'\x00', "red": b'\x30', "blue": b'\x03'}

display_rows = {b'\x00', b'\x01', b'\x02', b'\x03'}

eom = b'\xf7'  # End of message byte


def set_color(connection, strip, color):
    """

    :param connection: JLC connection object to send the command
    :param strip: int 0 - 7
    :param color: string from colors dict
    :return:
    """
    message = header + strips[strip] + set_color_command + colors[color] + colors[color] + eom
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
    #row_1_text = text[:10].center(10)
    #row_2_text = text[11:20].center(10)


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






