import Adafruit_BBIO.GPIO as GPIO
import time
import serial
import datetime
import math

LED0 = "USR0"
LED1 = "USR1"
LED2 = "USR2"
LED3 = "USR3"
GPIO.setup(LED0, GPIO.OUT)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)
GPIO.output(LED0, GPIO.LOW)
GPIO.output(LED1, GPIO.LOW)
GPIO.output(LED2, GPIO.LOW)
GPIO.output(LED3, GPIO.LOW)

ser = serial.Serial()

ser.port = "/dev/ttyO4"

ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
ser.parity = serial.PARITY_NONE  # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits

ser.timeout = 1  # non-block read

ser.xonxoff = False  # disable software flow control
ser.rtscts = False  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control

ser.writeTimeout = 2  # timeout for write

try:
    ser.open()
except Exception as e:
    print("error open serial port: " + str(e))
    exit()

if ser.isOpen():
    try:
        ser.flushInput()  # flush input  buffer
        ser.flushOutput()  # flush output buffer
    except Exception.e1:
        print("error to open serial port")

    time.sleep(0.5)  # give the serial port sometime to receive the data
    
    ATcommand="AT+ADDRESS=1\r\n" #set receiver to address 1
    ser.write(ATcommand)
    time.sleep(0.4)
    ATcommand="AT+CRFOP=0\r\n" #set power of receiver
    ser.write(ATcommand)
    time.sleep(0.4)
    ATcommand="AT+PARAMETER=12,3,4,4\r\n"
    ser.write(ATcommand)
    time.sleep(0.4)
    ser.flushInput()
    
    def findOtherNodes():
        na = otherNode()
        nb = otherNode()
        nc = otherNode()
        otherNodesOnNetwork=0 #variable is 0 if no other Nodes on network.
        otherNodeIDs = [] #create blank list to hold other Node IDs
        otherNodeObjects = [na, nb, nc] # create a list to hold other Node Objects
        timeToWait=time.time()+600 # time to wait to see if other nodes are transmitting, in seconds
        readyToTransmit=False
        while readyToTransmit==False:
            receivedMessage = ser.readline();
            while receivedMessage == "":
                receivedMessage = ser.readline();
                if time.time() > timeToWait and otherNodesOnNetwork==0:
                    ser.flushInput()
                    break
            if time.time() > timeToWait and otherNodesOnNetwork==0:
                ser.flushInput()
                break
            print(receivedMessage)
            file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
            ts=time.time()
            st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            file.write(st+ ",")
            file.write(receivedMessage)
            file.close()
            firstComma=receivedMessage.find(",")
            secondComma=receivedMessage.find(",",firstComma+1)
            thirdComma=receivedMessage.find(",",secondComma+1)
            fourthComma=receivedMessage.find(",",thirdComma+1)
            actualMessage=receivedMessage[secondComma+1:thirdComma]
            x=receivedMessage.find(";")
            receivedMessageID=receivedMessage[secondComma+1:x]
            try:
                if int(receivedMessageID) == 1 or int(receivedMessageID) == 2 or int(receivedMessageID) == 3 or int(receivedMessageID) == 4 or int(receivedMessageID) == 5 or int(receivedMessageID) == 6:
                    if int(receivedMessageID) not in otherNodeIDs:
                        otherNodeIDs.append(int(receivedMessageID))
                        x = otherNodeIDs.index(int(receivedMessageID))
                        otherNodeObjects[int(x)].setNodeID(int(receivedMessageID))
                        otherNodeObjects[int(x)].gotNewMessage()
                        otherNodesOnNetwork+=1
                    else:
                        x = otherNodeIDs.index(int(receivedMessageID))
                        otherNodeObjects[int(x)].gotNewMessage()
            except ValueError:
                print("bad message")
            if otherNodesOnNetwork > 0:
                readyToTransmit = True
                i = 0
                while i < len(otherNodeIDs):
                    if otherNodeObjects[i].timeStamp == 0:
                        readyToTransmit = False
                    i+=1
        while True: #gets to this step if ready to start transmitting
            file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
            ts=time.time()
            st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            file.write(st+ ",")
            file.write("Begin Attempt to transmit.\r\n")
            file.close()
            GPIO.output(LED0, GPIO.HIGH)
            selfTransmissionInterval=60 # sets the transmission interval of this node
            messageToSend="4;Hello From Four"  #########################################update here
            lengthofMSG=len(messageToSend)
            #while otherNodesOnNetwork == 0:
             #   ATcommand="AT+ADDRESS=4\r\n" #set transceiver address  #########################################update here
              #  ser.write(ATcommand)
               # time.sleep(2)
            #    ser.flushInput()
            #    ser.write("AT+SEND=1," + str(lengthofMSG) +"," + messageToSend + "\r\n")
            #    time.sleep(3)
            #    ser.flushInput()
            #    ATcommand="AT+ADDRESS=1\r\n" #set transceiver address
            #    ser.write(ATcommand)
            #    time.sleep(0.5)
            #    ser.flushInput()
            #    time.sleep(selfTransmissionInterval-(5.5))
            #    while time.time() < timeToWait:
            #        receivedMessage = ser.readline();
            #        while receivedMessage == "":
            #            receivedMessage = ser.readline();
            #            if time.time() > timeToWait:
            #                ser.flushInput()
            #                break
            #        print(receivedMessage)
            ser.flushInput()
            if otherNodesOnNetwork > 0:
                timeToWait=time.time()+(otherNodeObjects[0].transmissionInterval/2)
                print(timeToWait)
            i = 0
            while i < len(otherNodeIDs) and otherNodesOnNetwork > 0:
                i+=1
                receivedMessage = ser.readline();
                while receivedMessage == "":
                    receivedMessage = ser.readline();
                    if time.time() > timeToWait:
                        print("try again")
                        file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
                        ts=time.time()
                        st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        file.write(st+ ",")
                        file.write("Try again to sync with other nodes.\r\n")
                        file.close()
                        time.sleep(otherNodeObjects[0].transmissionInterval/10)
                        i = 0
                        ser.flushInput()
                        timeToWait=time.time()+(otherNodeObjects[0].transmissionInterval/2)
                        break
                file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
                ts=time.time()
                st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                file.write(st+ ",")
                file.write(receivedMessage)
                file.close()
            if otherNodesOnNetwork > 0:
                time.sleep(13)
            while True:
                ATcommand="AT+ADDRESS=4\r\n" #set transceiver address  #########################################update here
                ser.write(ATcommand)
                time.sleep(0.5)
                ser.flushInput()
                ser.write("AT+SEND=1," + str(lengthofMSG) +"," + messageToSend + "\r\n")
                file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
                ts=time.time()
                st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                file.write(st+ ",")
                file.write("Message Sent.\r\n")
                file.close()
                time.sleep(2)
                ser.flushInput()
                ATcommand="AT+ADDRESS=1\r\n" #set transceiver address
                ser.write(ATcommand)
                print("Message Sent.")
                time.sleep(0.5)
                ser.flushInput()
                timeToWait=time.time()+(selfTransmissionInterval-(3))
                while time.time() < timeToWait:
                    receivedMessage = ser.readline();
                    while receivedMessage == "":
                        receivedMessage = ser.readline();
                        if time.time() > timeToWait:
                            ser.flushInput()
                            break
                    if time.time() > timeToWait:
                        break
                    print(receivedMessage)
                    file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
                    ts=time.time()
                    st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    file.write(st+ ",")
                    file.write(receivedMessage)
                    firstComma=receivedMessage.find(",")
                    secondComma=receivedMessage.find(",",firstComma+1)
                    thirdComma=receivedMessage.find(",",secondComma+1)
                    fourthComma=receivedMessage.find(",",thirdComma+1)
                    x=receivedMessage.find(";")
                    rssi=receivedMessage[thirdComma+2:fourthComma]
                    rssi2=0
                    y=1 #Switch to 1 if not relay!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    try:
                        rssi2=int(rssi)
                    except ValueError:
                        y=1
                        
                    if rssi2 > 70 and y==0:
                        actualMessage=receivedMessage[x+1:thirdComma]
                        lengthofMSG = len(actualMessage)
                        ATcommand="AT+ADDRESS=4\r\n" #set transceiver to address 4 #set transceiver address  #########################################update here
                        ser.write(ATcommand)
                        time.sleep(5)
                        ser.flushInput()
                        file.write("Message retransmitted at 15 dBm. RSSI below -70 dBm.\r\n")
                        ser.write("AT+SEND=1," + str(lengthofMSG) +"," + actualMessage + "\r\n")
                        time.sleep(2)
                        ser.flushInput()
                        ATcommand="AT+ADDRESS=1\r\n" #set transceiver to address 1
                        ser.write(ATcommand)
                        time.sleep(0.5)
                        ser.flushInput()
                    file.close()
            
            
    class otherNode:
        def __init__(self):
            self.ID=0
            self.transmissionInterval=0
            self.messageTimes = []
            self.numberOfMessage=0
            self.timeStamp=0
            self.standardDev=0
            self.firstMSGTime=0
            self.recMSGTime=0
            self.x=0
        def setNodeID(self,newID):
            self.ID = newID
        def gotNewMessage(self):
            self.numberOfMessage+=1
            print(self.numberOfMessage)
            if self.firstMSGTime == 0:
                self.firstMSGTime = time.time()
            elif self.transmissionInterval == 0:
                self.recMSGTime = time.time()
                self.x=self.recMSGTime-self.firstMSGTime
                self.firstMSGTime=self.recMSGTime
                self.messageTimes.append(int(self.x))
                print(self.x)
                if len(self.messageTimes) > 3:
                    self.transmissionInterval = (sum(self.messageTimes)/len(self.messageTimes))
                    for i in self.messageTimes:
                        self.standardDev+=((i-self.transmissionInterval)**2)
                    self.standardDev*=(1/len(self.messageTimes))
                    self.standardDev=math.sqrt(self.standardDev)
                    if self.standardDev < 1: #this checks if you have outliers in your data set. Increase to allow for more variation. 
                        print(self.standardDev)
                    else: #if standard deviation isn't good, sorts the list and removes the highest number. Calculates average time and standard deviation again. This allows for one outlier in the data set.
                        self.messageTimes.sort(reverse=True)
                        del self.messageTimes[0]
                        self.transmissionInterval = (sum(self.messageTimes)/len(self.messageTimes))
                        for i in self.messageTimes:
                            self.standardDev+=((i-self.transmissionInterval)**2)
                        self.standardDev*=(1/len(self.messageTimes))
                        self.standardDev=math.sqrt(self.standardDev)
                        if self.standardDev > 1: #checks standard deviation again.
                            clear(self.messageTimes)
                            self.transmissionInterval = 0
            elif self.timeStamp == 0:
                self.timeStamp=time.time()
                file = open("/var/lib/cloud9/Hopkins/Data.txt","a")
                ts=time.time()
                st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                file.write(st+ ",")
                file.write("Node ")
                file.write(str(self.ID))
                file.write(" transmission interval calculated to be ")
                file.write(str(self.transmissionInterval))
                file.write("\r\n")
                file.close()
                print(self.transmissionInterval)

    while True:
        GPIO.output(LED0, GPIO.LOW)
        GPIO.output(LED1, GPIO.LOW)
        GPIO.output(LED2, GPIO.LOW)
        GPIO.output(LED3, GPIO.LOW)
        findOtherNodes()

        break

else:
    print("can't open serial port")