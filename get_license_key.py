# Get a UID/serial number from the host Windows PC that this application is running on

import subprocess

VENDOR = "CAL-JLC"
TITLE = "Get License Key"
CONTACT = "contact.caljlc@gmail.com"
VERSION = "0.1"


def get_host_uid():
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()


if __name__ == '__main__':
    print(2 * "\n", 45*"#", "\n         {}: {}".format(VENDOR, TITLE), "\n", 45*"-", sep="")
    print("email this key to {}:".format(CONTACT))
    print("Key =", get_host_uid())

