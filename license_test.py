# Licensing test

import terminal_formatter as terminal
import licensing

# Key used for encryption, this must be kept secret,
#   - Do not make source code that contains a hardcoded key public!
#   - This was generated using licensing.generate_key()
KEY = b'edj9nzeY0aEKtVZjE_aCZbak2dUz_ULcsaCUA4krbIg='


def create_license_file(key=KEY):
    host_uid = licensing.get_host_uid()
    licensing.create_license_file(host_uid, key)


if __name__ == '__main__':
    terminal.print_heading("licensing test", "0.1")

    create_license_file()  # Creates a new license file

    valid = licensing.validate_license(KEY)  # Checks if license file present and valid for host UID

    if valid:
        terminal.print_heading("WELCOME", "You're in!")
    else:
        print("This machine is not licensed to run this code!")

