# Utilities for formatting output to terminal

TITLE = "Terminal Formatter"
VERSION = "0.1"

PADDING = 4


def print_heading(title, version, padding=PADDING):

    heading = "{}, version {}".format(title, version)
    width = len(heading) + padding * 2

    print("\n\n", width * "#", "\n", padding * " ", heading, "\n", width * "=", sep="")


if __name__ == '__main__':
    print_heading(TITLE, VERSION)