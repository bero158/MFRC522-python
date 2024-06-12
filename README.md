# mfrc522

## Changes
This is an extension of the original library.
Changes:
- Reading Cascade tags (Anticoll 1, 2 and 3) implemented
- Integration with another solutions which use GPIO ports (Close() closes only RST pin)
- Simple debouncer added for blocking ID reading
- Timing improved for faster ID reading

A python library to read/write RFID tags via the budget MFRC522 RFID module.

This code was published in relation to a [blog post](https://pimylifeup.com/raspberry-pi-rfid-rc522/) and you can find out more about how to hook up your MFRC reader to a Raspberry Pi there.

## Installation

Until the package is on PyPi, clone this repository and run `python setup.py install` in the top level directory.

## Example Code

The following code will read a tag from the MFRC522

```python
from time import sleep
import sys
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

try:
    while True:
        print("Hold a tag near the reader")
        id, text = reader.read()
        print("ID: %s\nText: %s" % (id,text))
        sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
```
