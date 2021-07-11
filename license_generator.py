# License file generator for CAL-JLC
# CAL-JLC checks for the presence of a valid license file at start up
# The license file needs to be in the same location as the CAL-JLC application file
#   and validates against the UID of the host machine running the application.
#   The file needs to have a ".license" extension
#   The file is supplied with a filename matching the non-encrypted host UID, but can be changed to anything to help
#     users manage multiple files.
#   The file also contains a customer name and system reference that will be displayed on the JLC panel.

# If the CAL-JLC application cannot find a valid license file, it will run in evaluation mode (it will stop after 10 minutes).
#   When running in evaluation mode, it will display the users "product key" (the uid of their machine) and copy it to
#   their clipboard, prompting them to email it to support.caljlc@gmail.com
#   - I need to then run this application, entering their UID, customer name and system name to generate a file I can
#       email back to them to unlock unlimited running of the application.

import licensing
import terminal_formatter as term

TITLE = "CAL-JLC License file generator"
VERSION = "1.0"

if __name__ == '__main__':
    term.print_heading(TITLE, VERSION)
    customer = input("Enter customer name: ")
    system = input("Enter system name: ")
    host_uid = input("Enter customer's product key: ")
    licensing.create_license_file(host_uid, licensing.key, customer, system)