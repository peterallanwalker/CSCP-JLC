
import JLC_utils as utils
import time

class Display:

    default_color = utils.COLORS_7_BIT["light-blue-7"]

    header = b'\xf0\x15\x26\x04'
    strips = (b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07')
    set_color_command = b'\x00'
    set_text_command = b'\x03'
    colors = {"off": b'\x00', "red": b'\x30', "blue": b'\x03'}
    display_rows = (b'\x00', b'\x01', b'\x02', b'\x03')
    eom = b'\xf7'  # End of message byte

    def __init__(self, strip, header="", label="", color=default_color):
        """ Assumes displays are in 4 * 10 char lines mode
            header is diplayed on line 1
            label is displayed on lines 3 & 4

        """
        self.strip = strip
        self.header = header
        self.label = label
        self.color = color
        self.full_text = ""

        self._format_text()

    def _format_text(self):
        row1 = self.header[:10].center(10)
        row2 = 10 * " "
        row3 = self.label[:10].center(10)
        row4 = self.label[11:20].center(10)
        self.full_text = row1 + row2 + row3 + row4

    def __str__(self):
        return "JLC_display object, Strip: {}, header: {}, label:{}, full text: {}, full text length: {}, color: {}"\
            .format(self.strip, self.header, self.label, self.full_text, len(self.full_text), self.color)

    def set_header(self, header):
        self.header = header
        self._format_text()

    def set_label(self, label):
        self.label = label
        self._format_text()

    def write_text(self, connection):
        message = Display.header + Display.strips[self.strip] + Display.set_text_command + Display.display_rows[0] + bytes(self.full_text, 'utf-8') + Display.eom
        connection.send(message)
        time.sleep(0.4)  # Ensure time to complete the write # TODO - Improve on this

    def write_color(self, connection):
        message = Display.header + Display.strips[self.strip] + Display.set_color_command + bytes([self.color, self.color]) + Display.eom
        connection.send(message)
        time.sleep(0.4)  # Ensure time to complete the write # TODO - Improve on this


if __name__ == '__main__':
    print("JLC_display_03")

    import JLC_connection_lan as connection
    conn = connection.Connection("192.168.200.114", 49300)

    while not conn.status == "Connected":
        pass

    for i in range(8):
        display = Display(i)
        display.set_header("TEST" + str(i))

        display.set_label("TESTTESTTEST" + str(i))

        display.write_text(conn)

        display.write_color(conn)
