import time

import RPi.GPIO as GPIO
import MFRC522
import signal
import socket
import struct


class NFCClient:

    # RFID package ID's
    AUTH_REQ = 101
    MASTER_REQ = 102
    ADD_TAG = 103
    DELETE_TAG = 104
    
    # Button ID's
    MASTER_B = 8
    ADD_TAG_B = 10
    DELETE_TAG_B = 12
    
    # LEDS
    ERR_LED = 3
    SUCC_LED = 5

    # TAGS
    TAG_SIZE = 10
<<<<<<< HEAD
    
    #TIMEOUTS
    CLIENT_TO = 10
    SOCKET_TO = 5
=======
>>>>>>> 964d389daf63ef7e8fca9987688fbdeed1635911

    def __init__(self, ip_address, port):

        self.ip_address = ip_address
        self.port = port
        self.server_address = (self.ip_address, self.port)
        self.master_state = False
<<<<<<< HEAD
        self.client_timeout = self.CLIENT_TO
        self.button_timeout = self.SOCKET_TO
=======
        self.client_timeout = 5
        self.button_timeout = 5
>>>>>>> 964d389daf63ef7e8fca9987688fbdeed1635911
        self.sock = ""
        self.card_reader = MFRC522.MFRC522()

    def init_client(self):

        try:
            print("Starting NFC client ...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Socket creation: Socket created!")
            self.sock.settimeout(self.client_timeout)
            print("Client started!")

            GPIO.setup(self.MASTER_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.ADD_TAG_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.DELETE_TAG_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.ERR_LED, GPIO.OUT)
            GPIO.setup(self.SUCC_LED, GPIO.OUT)
            GPIO.output(self.ERR_LED, False)
            GPIO.output(self.SUCC_LED, False)

        except socket.error as err:
            print("Error starting client: {}".format(err))

    def run_client(self):

        while True:

            if not GPIO.input(self.MASTER_B) and not self.master_state:
                self.master_state = True
                timer = time.time()
                print("Master button pressed")
                
		if self.master_state:
		    if (time.time() - timer) > self.button_timeout:
		        self.master_state = False

            card_uid = self.read_card()

            if card_uid:

                if self.master_state:
                    self.handle_master_state(card_uid)
                else:
                    self.handle_authentication(card_uid)

    def read_card(self):

        # Scan for cards
        (status, TagType) = self.card_reader.MFRC522_Request(self.card_reader.PICC_REQIDL)

        # If a card is found
        if status == self.card_reader.MI_OK:
            print("Card detected")

        # Get the UID of the card
        (status, uid) = self.card_reader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == self.card_reader.MI_OK:
            return uid

    @staticmethod
    def __create_package(code, size, data):
        # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.
        code = struct.pack('>h', code)
        size = struct.pack('>h', size)
        data = struct.pack('>' + 'h' * len(data), *data)
        package = code + size + data

        print("Package created -> " + (package))
        
        p = package
        
        code = struct.unpack('>h', p[:2])[0]
        size = struct.unpack('>h', p[2:4])[0]
        data = struct.unpack('>' + 'h' * int(size / 2), p[4:size + 4])
        
        print(data)
<<<<<<< HEAD

        tag_str = ""

        for n in range(len(data)):
            tag_str += str(data[n]) + ","
            
        tag_str = tag_str[:-1]
        print(tag_str)
=======
>>>>>>> 964d389daf63ef7e8fca9987688fbdeed1635911
        

        return package

    def handle_authentication(self, card_uid):	

        package = self.__create_package(self.AUTH_REQ, self.TAG_SIZE, card_uid)
        self.sock.sendto(package, self.server_address)
        
        print("Card authentication requested")
        
        response = self.handle_server_response()

        if response == 1:
            print("AUTHENTICATED")
            GPIO.output(self.SUCC_LED, True)
            time.sleep(1)
            GPIO.output(self.SUCC_LED, False)
        else:
            print("AUTHENTICATION FAILED")
            GPIO.output(self.ERR_LED, True)
            time.sleep(1)
            GPIO.output(self.ERR_LED, False)
            

    def handle_server_response(self):

        try:

            package = self.sock.recvfrom(40)
            p = package[0]
            address = package[1]

            print("Received {} bytes from {}".format(len(package), address))

            # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.

            code = struct.unpack('>h', p[:2])[0]
            size = struct.unpack('>h', p[2:4])[0]
            data = struct.unpack('>' + 'h' * int(size / 2), p[4:size + 4])
<<<<<<< HEAD
            
            return data[0]
=======

            return data
>>>>>>> 964d389daf63ef7e8fca9987688fbdeed1635911

        except socket.timeout as err:
            print("Socket err: ", err)
            print("SERVER RESPONSE TIMED OUT\n")
            GPIO.output(self.ERR_LED, True)
            time.sleep(1)
            GPIO.output(self.ERR_LED, False)
            self.run_client()

    def authenticate_master(self, master_key):

        package = self.__create_package(self.MASTER_REQ, self.TAG_SIZE, master_key)
        self.sock.sendto(package, self.server_address)
        response = self.handle_server_response()

        if response == 1:
            print("MASTER KEY AUTHENTICATED")
            GPIO.output(self.SUCC_LED, True)
            time.sleep(1)
            GPIO.output(self.SUCC_LED, False)
            return True
        else:
            print("AUTHENTICATION MASTER KEY FAILED")
            GPIO.output(self.ERR_LED, True)
            time.sleep(1)
            GPIO.output(self.ERR_LED, False)
            return False

    def handle_master_state(self, master_key):

        button_activated = False
        add_tag_activated = False
        delete_tag_activated = False
        print("On master handle auth")
        master_authenticated = self.authenticate_master(master_key)

        if master_authenticated:

            timer = time.time()

            while (time.time() - timer < self.client_timeout) and not button_activated:

                add_tag = GPIO.input(self.ADD_TAG_B)
                delete_tag = GPIO.input(self.DELETE_TAG_B)

                if not add_tag and not add_tag_activated:
                    print("Add tag button pressed")
                    add_tag_activated = True


                if not delete_tag and not delete_tag_activated:
                    print("Delete tag button pressed")
<<<<<<< HEAD
                    delete_tag_activated = True
=======
                    deelte_tag_activated = True
>>>>>>> 964d389daf63ef7e8fca9987688fbdeed1635911
                
                if delete_tag_activated or add_tag_activated:
					
		    uid = self.read_card()
					
                    if uid:
						
		        if (add_tag_activated):
			    package = self.__create_package(self.ADD_TAG, self.TAG_SIZE, uid)
			    self.sock.sendto(package, self.server_address)
			    button_activated = True
							
		        if (delete_tag_activated):
<<<<<<< HEAD
			    package = self.__create_package(self.DELETE_TAG, self.TAG_SIZE, uid)
=======
			    package = self.__create_package(self.ADD_TAG, self.TAG_SIZE, uid)
>>>>>>> 964d389daf63ef7e8fca9987688fbdeed1635911
			    self.sock.sendto(package, self.server_address)
		            button_activated = True
		            
            if button_activated:

                response = self.handle_server_response()

                if response == 1:
                    print("ADD/DELETE successful")
                    self.master_state = False
                    GPIO.output(self.SUCC_LED, True)
                    time.sleep(1)
                    GPIO.output(self.SUCC_LED, False)
                    return True

                else:
                    print("FAILED ADDING/DELETING")
                    self.master_state = False
                    GPIO.output(self.ERR_LED, True)
                    time.sleep(1)
                    GPIO.output(self.ERR_LED, False)
                    return False
            else:
                print("No action button pressed or reading timeout")
                GPIO.output(self.ERR_LED, True)
                time.sleep(1)
                GPIO.output(self.ERR_LED, False)
                self.master_state = False
        else:
            self.master_state = False

