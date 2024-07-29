#import modbus
import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer


def count(num,id):

        if id == 0:
            Port = "/dev/ttyUSB0"
        if id == 1:
            Port = "/dev/ttyUSB1"

        client = ModbusClient( method = 'rtu', port = Port, stopbits = 1, bytesize = 8, baudrate=9600 , parity= 'N')
        #print(client.connect())

        num_digits = len(str(num))
        #print(num_digits)
        if num_digits == 1:
                A = 32
                B = 32
                C = 32
                D = num + 48

        if num_digits == 2:
                A = 32
                B = 32
                C = num // 10 + 48
                D = num % 10 + 48

        if num_digits == 3:
                A = 32
                B = num // 100 + 48
                C = num % 100 // 10 + 48
                D = num % 10 + 48

        if num_digits == 4:
                A = num // 1000 + 48
                B = num % 1000 // 100 + 48
                C = num % 100 // 10 + 48
                D = num % 10 + 48
        #print(A,B,C,D)
        wv = client.write_registers(0,[A, B, C, D],count=4,unit=1)


        client.close()

#999
def warn(x):

        Port = "/dev/ttyUSB0"


        client = ModbusClient( method = 'rtu', port = Port, stopbits = 1, bytesize = 8, baudrate=9600 , parity= 'N')
        #print(client.connect())
        if x == 999:
                #999
                wv = client.write_registers(0,[0x0020, 0x0039, 0x0039, 0x0039],count=4,unit=1)
        else:
        #fuck
        #wv = client.write_registers(0,[0x0066, 0x0055, 0x0043, 0x004b],count=4,unit=1)
                #不亮
                wv = client.write_registers(0,[0x0020, 0x0020, 0x0020, 0x0020],count=4,unit=1)

        client.close()



#32 = " "
#48 = 0
#65 = A
