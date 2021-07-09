# Utilities for formatting output to terminal

TITLE = "Terminal Formatter"
VERSION = "0.1"

PADDING = 4


def print_heading(title, version, additional=("",), padding=PADDING):

    heading = "{}, version {}".format(title, version)

    width = len(heading)

    for line in additional:
        if len(line) > width:
            width = len(line)

    width += padding * 2

    print("\n\n", width * "#", "\n", padding * " ", heading, "\n", padding * " ", len(heading) * "-", sep="")

    for line in additional:
        print(padding * " ", line, sep="")

    print(width * "=")


if __name__ == '__main__':
    additional_text = ("some more text", "line3", "a very long string of text that is longer than the heading")
    print_heading(TITLE, VERSION, additional_text)