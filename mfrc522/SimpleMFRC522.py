# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import time
import RPi.GPIO as GPIO


class SimpleMFRC522:

    READER = None
    debouncer = None

    KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    # KEY = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
    # KEY = [0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5]
    
    BLOCK_ADDRS = [8, 9, 10]

    def __init__(self,pin_mode=GPIO.BOARD, pin_rst=-1,debugLevel='DEBUG'):
        self.READER = MFRC522(pin_mode=pin_mode, pin_rst=pin_rst, debugLevel=debugLevel)

    def read(self):
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block()
        return id, text

    def read_id(self):
        """
        Reads the tag ID from the RFID tag.

        Returns:
            id (int): The tag ID as an integer.
        """
        id = None
        errorCount = 0
        while (not id) or (self.debouncer == id):
            time.sleep(0.2)
            id = self.read_id_no_block()
            if self.debouncer:
                if id:
                    errorCount = 0
                else:
                    errorCount += 1
                    # every second reading is an error so we're waiting for at least two invalid reading here.
                    if errorCount > 2:
                        self.debouncer = None
        self.debouncer = id
        return id

    def read_id_no_block(self):
        # Send request to RFID tag
        (status, TagType) = self.READER.Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None

        uid = self.READER.SelectTagSN()
        return uid

    def read_no_block(self):
        uid = self.read_id_no_block()
        if not uid:
            return None, None
        status = self.READER.Authenticate(
            self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
        text_read = ''
        if status == self.READER.MI_OK:
            for block_num in self.BLOCK_ADDRS:
                block = self.READER.ReadTag(block_num)
                if block:
                    text_read += bytes(block).decode("ascii")
        self.READER.StopCrypto1()
        return uid, text_read

    def write(self, text):
        id, text_in = self.write_no_block(text)
        while not id:
            id, text_in = self.write_no_block(text)
        return id, text_in

    def write_no_block(self, text):
        uid = self.read_id_no_block()
        if not uid:
            return None, None
        # self.READER.SelectTag(uid)
        status = self.READER.Authenticate(
            self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
        self.READER.ReadTag(11)
        if status == self.READER.MI_OK:
            data = bytearray()
            data.extend(bytearray(text.ljust(
                len(self.BLOCK_ADDRS) * 16).encode('ascii')))
            i = 0
            for block_num in self.BLOCK_ADDRS:
                self.READER.WriteTag(block_num, data[(i*16):(i+1)*16])
                i += 1
        self.READER.StopCrypto1()
        return uid, text[0:(len(self.BLOCK_ADDRS) * 16)]

    def close(self):
        self.READER.Close()