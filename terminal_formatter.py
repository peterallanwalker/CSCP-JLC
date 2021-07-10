# Utilities for formatting output to terminal

TITLE = "Terminal Formatter"
VERSION = "0.2"

PADDING = 4


def print_heading(title, version, additional=("",), padding=PADDING):

    heading = "{}, version {}".format(title, version)

    width = len(heading)

    for line in additional:
        if len(line) > width:
            width = len(line)

    max_width = width + (padding * 2)

    #print("\n\n", width * "#", "\n", padding * " ", heading, "\n", padding * " ", len(heading) * "-", sep="")
    print("\n", max_width * "#", "\n", padding * " ", heading, "\n", padding * " ", width * "-", sep="")

    for line in additional:
        print(padding * " ", line, sep="")

    print(max_width * "=")


def print_footer(*args, padding=PADDING):
    max_text_width = 0
    for line in args:
        if len(line) > max_text_width:
            max_text_width = len(line)

    full_width = max_text_width + (padding * 2)

    print("\n", full_width * "=", sep="")

    for line in args:
        print(padding * " ", line)

    print(full_width * "#")


if __name__ == '__main__':
    additional_text = ("some more text", "line3", "a very long string of text that is longer than the heading")
    print_heading(TITLE, VERSION, additional_text)