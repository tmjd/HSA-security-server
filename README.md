# HSA security server

This is the brains behind my home build security system.  It would communicate
with an Arduino (multiple) that was running some other custom code.  The
Arduino's would transmit the statuses of motion and other sensors and this
server would keep track of them.  The Arduino's would also take input and
display output to/from the user so this server would also process and send
that information.

This should really have some better documentation but at this point I think
this is just for posterity as some of my hardware got broken so I'm looking
forward to perhaps switching to Raspberry Pi's and possibly rewriting this
in go.
