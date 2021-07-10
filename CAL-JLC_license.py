# CAL-JLC License
# Reads the UID of the host machine running this simple program
# Intention of providing as .exe download, asking users to email the result
# that I can return as an encoded license file.

import pyperclip  # For copying/pasting to/from Windows clipboard

import terminal_formatter as term
import web_info

from licensing import get_host_uid

TITLE = "CAL-JLC License"
VERSION = "1.0"

if __name__ == '__main__':

    host_uid = get_host_uid()

    info = "Product key: {}".format(host_uid)
    prompt2 = "copied to your clipboard, ready to paste..."
    prompt = "email product key to {} to activate".format(web_info.CONTACT)

    term.print_heading(TITLE, VERSION, (info, prompt2, prompt))

    # Copy host uid to host machine's clipboard, making it easier for users to paste the result into an email
    pyperclip.copy(host_uid)

