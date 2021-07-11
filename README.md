# CSCP-JLC

Provides two-way control between audio mixers supporting the CSCP protocol and
JL Cooper control panels.

The application is available as a Windows exe to download from https://caljlc.github.io/CAL-JLC/

Tested with JL Cooper Eclipse MXL2.

The default IP address for the JL Cooper panel is 192.168.200.114, and the default port is
49300.

This application will work with the default JL Cooper values, or you can change the IP address
and/or port if preferred. 

JLC config can be viewed or changed by entering its IP address into a browser 

If the IP address of teh JL Cooper panel is not known, it can be reset to default by holding down the
3 white buttons in strip 8 while powering up the unit. The unit will indicate when it has reset,
wait for it to indicate it is ready to be repowered then power off and back on again for the 
default settings to be applied.

Connect the PC this application is running on the the Ethernet port of the JLC panel and one 
on the mixer, either directly or via a network, ensuring the PC has IP address/es configured that are compatible
/ reachable by the addresses set on both the mixer and the JLC panel.


