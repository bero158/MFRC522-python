# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import RPi.GPIO as GPIO
  
class SimpleMFRC522:

  READER = None
  debouncer = None

  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  BLOCK_ADDRS = [8, 9, 10]
  
  def __init__(self):
    self.READER = MFRC522()
  
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
        while (not id) or (self.debouncer == id) :
            time.sleep(0.2)
            id = self.read_id_no_block()
            if self.debouncer:
                if id:
                    errorCount = 0
                else:
                    errorCount += 1
                    if errorCount > 2: #every second reading is an error so we're waiting for at least two invalid reading here.
                        self.debouncer = None
        self.debouncer = id
        return id

  
  def read_id_no_block(self):
        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None
        
        uid = self.MFRC522.SelectTagSN()
        return uid
  
  def read_no_block(self):
    uid = self.read_id_no_block()
    if not uid:
        return None, None
    id = self.uid_to_num(uid)
    self.READER.MFRC522_SelectTag(uid)
    status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
    data = []
    text_read = ''
    if status == self.READER.MI_OK:
        for block_num in self.BLOCK_ADDRS:
            block = self.READER.MFRC522_Read(block_num) 
            if block:
                data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
    self.READER.MFRC522_StopCrypto1()
    return id, text_read
    
  def write(self, text):
      id, text_in = self.write_no_block(text)
      while not id:
          id, text_in = self.write_no_block(text)
      return id, text_in

  def write_no_block(self, text):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
      self.READER.MFRC522_Read(11)
      if status == self.READER.MI_OK:
          data = bytearray()
          data.extend(bytearray(text.ljust(len(self.BLOCK_ADDRS) * 16).encode('ascii')))
          i = 0
          for block_num in self.BLOCK_ADDRS:
            self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
            i += 1
      self.READER.MFRC522_StopCrypto1()
      return id, text[0:(len(self.BLOCK_ADDRS) * 16)]
      
  def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n
