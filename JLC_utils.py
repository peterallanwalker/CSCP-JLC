

# "Headers" - JLC control messages begin with a strip ID. Strips 1-8 have the following IDs:
JLC_STRIPS = (176, 177, 178, 179, 180, 181, 182, 183)

JLC_CONTROLS = {7: "fader_move",   # 0x07 is a fader move command
                70: "cut_toggle",
                }

CSCP_CONTROLS = {"fader_move": 7,  # TODO, better data storage wihtout the duplication
                 "cut_toggle": 70,
                 }

COLORS_7_BIT = {"off": 0,
                "dark-blue": 1,
                "medium-blue": 2,
                "bright-blue": 3,
                "bright-blue2": 7,

                "light-blue": 5,
                "light-blue-2": 6,
                "light-blue-3": 10,
                "light-blue-4": 11,
                "light-blue-5": 15,  # Nice color, good text contrast
                "light-blue-6": 26,
                "light-blue-7": 31,  # Nice color, good text contrast
                "light-blue-8": 47,  # Nice color, good text contrast
                "pale-blue": 21,
                "pale-blue-2": 27,
                "pale-blue-3": 42,
                "pale-blue-4": 63,
                "turquoise": 9,
                "turquoise-2": 13,
                "turquoise-3": 14,  # Nice color, good text contrast
                "turquoise-4": 29,
                "turquoise-5": 30,
                "turquoise-6": 45,
                "turquoise-7": 46,  # good contrast
                "pale-turquoise": 25,

                "dark-green": 4,
                "dark-green-2": 8,
                "dark-green-3": 24,
                "bright-green": 12,
                "green": 28,  # Nice color, good text contrast
                "green-2": 44,
                "green-yellow": 60,

                "purple": 17,
                "purple-2": 35,
                "light-purple": 18,
                "light-purple-2": 33,
                "light-purple-3": 34,
                "light-purple-4": 38,
                "light-purple-5": 39,
                "light-purple-6": 43,
                "light-purple-7": 51,
                "light-purple-8": 55,  # good contrast
                "light-purple-9": 59,  # good contrast
                "blue-purple": 19,
                "blue-purple-2": 22,
                "blue-purple-3": 23,
                "pale-purple": 37,
                "pale-purple-2": 54,
                "pale-purple-3": 58,

                "dark-red": 32,
                "medium-red": 48,
                "orange": 52,
                "brown": 16,  # dark orange
                "light-brown": 36,
                "yellow-green": 20,
                "yellow-green-2": 40,
                "yellow": 56,

                "pink": 49,
                "light-pink": 53,
                "purple-pink": 50,

                "pale-white": 41,
                "pale-white-2": 57,
                "white-green": 61,
                "white-blue": 62,
                }
