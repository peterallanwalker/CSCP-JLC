# Get a UID/serial number from the host Windows PC that this application is running on

import subprocess

TITLE = "Get host PC's UID"
VERSION = "0.1"


def get_host_uid():
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()


if __name__ == '__main__':
    print(2 * "\n", 35*"#", "\n   {}, V{}".format(TITLE, VERSION), "\n", 35*"-", sep="")
    print("This PC's ID =", get_host_uid())
