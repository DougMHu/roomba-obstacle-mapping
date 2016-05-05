import serial

# Open serial connection with USB port
ser = serial.Serial('/dev/ttyUSB0')
ser.close()