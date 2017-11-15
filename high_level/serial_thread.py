import threading
import sys
import glob
import serial
import time

from Queue import Queue, Full, Empty

def read_data(serial):
	if serial is None:
		return []
	STATUS_PACKET = []
	try:
		# ser.port = str( self.Serial_port_combo.currentText() )
		if not serial.is_open:
			print "Serial port is not open."
		elif serial.is_open:
			while serial.inWaiting():
				STATUS_PACKET.append(ord(serial.read()))
			if len(STATUS_PACKET) > 0:
				print "RECIEVE<< ",STATUS_PACKET
	except Exception as e:
		print e
	finally:
		return STATUS_PACKET

def write_data(serial, INSTRUCTION_PACKET):
	if serial is None:
		return
	try: 
		if not serial.is_open:
			print "Serial port is not open."
		elif serial.is_open and len(INSTRUCTION_PACKET) > 0:
			INSTRUCTION_PACKET.insert(3, len(INSTRUCTION_PACKET)-2)
			CHKSUM = 0
			for i in range(2, len(INSTRUCTION_PACKET)):
				CHKSUM += INSTRUCTION_PACKET[i]
			CHKSUM %= 256
			INSTRUCTION_PACKET.append(255-CHKSUM)
			serial.write(INSTRUCTION_PACKET)
			print "SEND>> ",INSTRUCTION_PACKET
	except Exception as e:
		print e
		print "Fail to send ", INSTRUCTION_PACKET

class Serilal_sender(threading.Thread):

	def __init__(self, serial, thread_name, sending_buffer, recieving_buffer,flag = None):
		super(Serilal_sender, self).__init__()
		self.serial = serial
		self.thread_name = thread_name
		self.flag  = flag
		self.sending_buffer = sending_buffer
		self.recieving_buffer = recieving_buffer

	def ReadData(self):
		Reading_packet = read_data(self.serial)
		try:
			self.recieving_buffer.put(Reading_packet)
		except Full as e:
			print e

	def WriteData(self):
		try:
			if self.sending_buffer.empty():
				return
			Sending_packet = self.sending_buffer.get()
			write_data(self.serial, Sending_packet)
			self.sending_buffer.task_done()
		except Empty as e:
			print e
		
	def run(self):
		print "running"
		self.flag.wait()
		while self.flag is None or self.flag.is_set():
			self.WriteData()
			time.sleep(0.05)
			self.ReadData()
			time.sleep(0.05)
		print "ending"

# class Contour_sender(threading.Thread):

# 	def __init__(self, serial, thread_name):