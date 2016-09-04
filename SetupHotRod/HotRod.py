import serial, sys, os, glob

def getSerialPorts():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
    
def getResponse(serialPort, endChar, maxChars = 32):
    ctr = 0
    response = ''
    try:
        c = serialPort.read(1)
        while c != endChar and c != 0 and ctr < maxChars:
            ctr += 1
            response += c
            # print "c = %02X" % (int(c))
            c = serialPort.read()
    except:
        pass
    return response

def findHotRod():
    HRPort = ''
    ports = getSerialPorts()

    for port in ports:
        try:
            response = ''
            sp = serial.Serial(port = port, baudrate = 9600, bytesize = serial.EIGHTBITS, parity= serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 0.2, write_timeout = 1)
            if (sp.write('?\n') == 2):
                response = getResponse(sp, '\n')
        except:
            pass
        if response.strip() == 'HotRod':
            HRPort = port
            break
        sp.close()
    return HRPort
    
