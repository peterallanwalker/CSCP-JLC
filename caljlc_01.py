

APPLICATION_VERSION = "V0.1, 10-5-21"


class MixData:

    def __init__(self, fader_strip_qty=8):
        self.strips = []
        for fader_strip in range(fader_strip_qty):
            self.strips.append(Strip(fader_strip))


class Strip:
    def __init__(self, strip_id):
        self.id = strip_id


def main():
    mix_data = MixData()
    for strip in mix_data.strips:
        print(strip.id)


if __name__ == '__main__':

    print(33*"#", "\n Calrec <-> JL Cooper translator", "\n ", APPLICATION_VERSION)

    main()
