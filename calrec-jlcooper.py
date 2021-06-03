# Attempt to get CSCP app to work with JLC panel
# - Panel is not appearing as a USB MIDI device
# --- Try different USB-A-B cable.
# ----- Not sure if it is supposed to, try some lower level USB comms.
# --- Try getting data over the Ethernet port, using code from CSCP Connection
# ----- Need an USB-Ethernet adaptor for my laptop!

# pyusb info: https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
# - Need to know vendor ID to find device?

# Consider signing up to JLC dev program?
# Checking out their site..
# https://www.jlcooper.com/_php/downloads.php?op=downloads#anchor-eclipseseries
# ... get the USB driver download dufus? (Doesn't mention this in the manual tho)

import usb.core
import usb.util

if __name__ == '__main__':
    print(20*'#' + "\nUSB comms test")

    # find our device
    dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

    # was it found?
    if dev is None:
        raise ValueError('Device not found')

    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    dev.set_configuration()

    # get an endpoint instance
    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]

    ep = usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match= \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

    assert ep is not None

    # write the data
    ep.write('test')
