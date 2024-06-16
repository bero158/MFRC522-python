from time import sleep
from mfrc522.SimpleMFRC522 import SimpleMFRC522
reader = SimpleMFRC522(pin_rst=7)

try:
    while True:
        print("Write text")
        text_in = input()
        print("Hold a tag near the reader")
        id, text = reader.write(text_in)
        print(f"ID: {bytes(id).hex()}\nText: {text}")
        sleep(5)
except KeyboardInterrupt:
    reader.close()
    raise