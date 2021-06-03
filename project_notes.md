

check CSCP messaging - echoes - recipient?
e.g. send a command to the mixer, what does it respond with?

... Have checked, on sending a command, e.g. fader position,
the mixer responds with an ACK
If the mixer needs to move the fader to get to the sent position,
it returns a message echoing back, recipient = controller

- need to ignore those.

-  Perhaps ignore any message that comes after an ack?
-- not sure that would be right, think need some form of timer to ignore
messages for a period ofter sent in one direction in relation to a specific control.

.. Not sure why faders are offset - strip 0 if affecting fader 2 not fader 1!?
.. CSCP GUI does the same??
... check older versions, check Brio
- Brio is OK - fader 0 = 1st strip
- Aretemis+ is also OK
- Just My Apollo+ so far has fader 0 being 2nd fader.

... Decide - do I need a mid-point data model?
.... would need to continually check full state, will that be fast enough?
.... might as well just push messaegs as they are recieved, and try to discard echoes,
based on time sent/recieved

Use CSCP COnnection to run thread storing incoming messages with methods to get received messages and to send messages
create a similar COnneciton class to run similar for JLC comms
have a main mixer class that manages the sending and the recieve buffers to prevent conflicts.

OK, got my JLC connection manager, but it is laggy running in a thread
same code not in a thread messages print in realtime ish
, but same code in a thread, get lags and delays.
... Is it this PC?? ... try my other laptop

... Now working with IP connection,
... basing on CSCP connection.

--------------------------
entry point - CSCP-JLC
creates a CSCP connection and a jlc connection
runs infinite loop checking for messages from jlc
if there is one, converts to cscp
----
... send to cscp and test
... create cscp - jlc and send.
... link the two and figure out how to prevent jitter
..... timsstamp messages?
.... could then down sample fader movements

.. make JLC connection as robust as CSCP one.

... add proper logging to help debug reported probs!


TEsted, got 2 way fader control working
is a bit laggy if moving lots of faders at same time
get a bit of jitter with bot directions enabled, but no where near as bad as reaper,
almost, but not quite acceptable!

- Try reducing fader data? (every other message)?
- Try receiving larger data chunks? or smaller data chunks (sock.recv(1024) currently)
- discard messages as son as not interested, e.g. fader messages?
- look for general efficiency savings in code
- C++ re-write :/
- reduce print statements / output to log file instead?

other todo - user input & saving of connection settings
fader mapping
fader labels
buttons
rotaries

EIther stop monitoring JLC connection for data, or ping it to get the FW version.

check memory/cpu  usage (run from cmd and from exe) (not within pycharm)

why does it take a while to get fader labels? - might be a delay before first ping, but CSCP GUI seems to get them straight away.
why dont all fader labels write to JLC at same time
- manual does say to wait between display writes... perhaps need to put them in a different queue?

SHOULD CLEAR TEXT AS WELL AS WRITING
MAYBE NEED TOS SET MODE BEFORE SENDING TEXT?

OPening 2 faders at once on JLC - one will track well, the other wont
 - check disabling touch?
 - See whats going on in DEBUG
 - OPENING LOTS IS LAGGY
 
 moving 8 faders on Apollo seems ok, slight jitter.
 (though fader 9 from surface doesnot control jlc other way works - my surface acting weird though, not 0-0)
 
... DONT SEEM TO GET ALL MESSAGES FROM JLC WHEN >1 FADER MOVED
... TRY LOOKING AT CHECKING TOUCH STATUS OR DISBALING TOUCH

... TRY SETTING DISPLAY MODE TO GIVE ACK WHEN READY
.. try holding display data in app / putting into a different queue or
... polling and sending data when not control messages to process.

TRY THE HAIRLESS MIDI SERIAL INTERFACE?

PLAN OF ATTACK:
- CHECK DEBUG WITHOUT CSCP FOR MOVING MULTIPLE JLC FADERS AT ONCE
-- try changing socket config, chunk size etc.
-- check touch settings
- PLAY WITH DISPLAYS MORE
-- try feedback mode
-- put CSCP messages into a seperate labels queue to process separate to fader messages

- control/strip mapping
-- DISCARD UNEEDED CSCP MESSAGED AT CONNECTION TO REDUCE THE MESSAGE LIST?

- SOrt the dropping of JLC on inactivity - send it a ping it will respond to! 

writing text to displays is VERY slow, and you have to wait for one to complete before sending further or they skip
-- check... its not blocking control data while updating displays???

WHY AM I NOT GETTING CONTROL JITTER?????
 - CSCP not echoing back????
 
 display colour updates seem fast
 display text updates are VERY slow... 
 
 for mulitple fader movement lag, poss try UDP? might have to time stamp/sequence number the messages
 
 OK, so writing text to the display IS VERY slow (5s+?) and blocks messaging while
 taking place, so can only really do it on startup
 
 ... do stirp mapping and display strip number at start.
  - Add a flush buffers method to connections
  - then can wait, process some labels then flush before starting main loop
  - put start up option to enable ccontrol in each direction / test JLC>CSCP only
  
 CONTROL FROM CSCP NOT GETTING ALL MESSAGES IN V_03
  - MOVE FADER ON CALREC, DOES NOT GET FULL END POSI SOMETIMES
  ORIIGNAL CSCP-JLC (v01) does not seem to do this though?
  
  
  OK, V04 working OK
  - speed up statup / wait for displays
  - when moving all faders on JLC together, sometimes they cocnflict snag
    -- change connection to filter incoming messages into separate queues?
    -- then can block and flush CSCP messages for n time after JLC messages for same strip
    -- read/set JLC fader positions at statup
    
    tidy and package V0.4
    rework connection / manage queues/write access for v0.5
    
    
    CHECK WERE NOT TIMING OUT ON LACK OF JLC DATA / FIX PING
    
    # TODO - TRY STRATING JLC CONNECTION FIRST - PERHAPS FIRST THREAD GETS PRIORITY?
    
    
    ALSO!!!!!! ...
     - create a CSCP python library????? 
     https://levelup.gitconnected.com/turn-your-python-code-into-a-pip-package-in-minutes-433ae669657f
     
     pyCSCP - 
     
     from CSCP import Connection, encode, decode
     
     
     ---NEW TODO ---
     Get USB working as an option
     Add email contact 
     add ITN specific detail
     
     get on buttons working
     refresh displays, either when changed or when 3 buttons held (display buttons)
     
     get mixer name at startup, put that on top left display, or CAL-JLC, ITN, Mixer Name 
     
 Tried and failed to get display feedback enabled
 and returning F8 when display color write completed
 so will have to rely on setting small delay between writes
 
 
 MOVING faders, get snapp back/fighting if you dont maintain touch contact.
 LABELS - PICMING UP THE CENTE OR ROW 2 LABEL - ACTUALLY, THINK WE ARE STRIPPING FIRST CHAR OF LINE 2
 JLC ON BUTTON LEDS NOW LIGHTING BUT NEEDS TOGGLING ON MIXER TO SYNC - SHOULD PUSH STARTUP / REQUEST STATE FROM MIXER
 JLC BUTTON PRESS WORKS AS WELL BUT MOMENTARY - DOWN = CUT, RELEASE = UNCUT
 
 CSCP converted TO JLC:  JLC Message: Strip - 176, Operation - 70, Value - 0, Encoded - b'\xb0F\x00'

 CSCP converted TO JLC:  JLC Message: Strip - 176, Operation - 70, Value - 0, Encoded - b'\xb0F\x00'
 
 ----------------------
 FIX ON BUTTON RELEASE - DONE
 
 GET CUT STATES AND FADER POSITIONS AT STARTUP AND WRITE TO JLC
 CHECK RECONNECT/RESET OF JLC AND CALREC
 REMOVE EXCESS DEBUG, BUILD AN EXE
 CREATE NEW VERSIO AND REFATOR, TIDY, BUILD RUST VERSION
 ADD LOGGING
 ADD OTHER BUTTONS< ROTARIES ETC
 IMPROVE DISPLAY UPDATES
 
 TBD - TWO WAY FADER - JLC SNAP BACK WHEN TOUCH NOT MAINTAINED.    
 
 ----------------------------------------
 V0.8 is released and given to ITN.
 github page is up,
 download link working now
 
 TODO - Setup paypal link / might need to change paypal account, 
 creaete a 0.9 release that does not say ITN but says evaluation copy
 ... have start screen stating eval copy, with a pause and links to the site/contact info.
 
 put feature requests on the site page-
 label updates
 more resilient sockcet connections
 display colour choice
 get PFL working, use display buttons for cut / set colours
 rotaries
 routing buttons
 
 automated events?
 
 refactor code base
 re-write in Rust?
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
     
