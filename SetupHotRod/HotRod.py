import serial, sys, os, glob, threading

HRCodes = {
    'HR_ONE_PLAYER'          :0x16,
    'HR_TWO_PLAYER'          :0x1E,
    'HR_LEFT_JOYSTICK_UP'    :0x75,
    'HR_LEFT_JOYSTICK_DOWN'  :0x72,
    'HR_LEFT_JOYSTICK_RIGHT' :0x74,
    'HR_LEFT_JOYSTICK_LEFT'  :0x6B,
    'HR_LEFT_BUTTON_SIDE'    :0x26,
    'HR_LEFT_BUTTON_1'       :0x14,
    'HR_LEFT_BUTTON_2'       :0x11,
    'HR_LEFT_BUTTON_3'       :0x29,
    'HR_LEFT_BUTTON_4'       :0x12,
    'HR_LEFT_BUTTON_5'       :0x1A,
    'HR_LEFT_BUTTON_6'       :0x22,
    'HR_LEFT_BUTTON_7'       :0x21,
    'HR_RIGHT_JOYSTICK_UP'   :0x2D,
    'HR_RIGHT_JOYSTICK_DOWN' :0x2B,
    'HR_RIGHT_JOYSTICK_RIGHT':0x34,
    'HR_RIGHT_JOYSTICK_LEFT' :0x23,
    'HR_RIGHT_BUTTON_SIDE'   :0x25,
    'HR_RIGHT_BUTTON_1'      :0x1C,
    'HR_RIGHT_BUTTON_2'      :0x1B,
    'HR_RIGHT_BUTTON_3'      :0x15,
    'HR_RIGHT_BUTTON_4'      :0x1D,
    'HR_RIGHT_BUTTON_5'      :0x24,
    'HR_RIGHT_BUTTON_6'      :0x54,
    'HR_RIGHT_BUTTON_7'      :0x5B,
}

KBKeys ={
    'KEY_SPACEBAR'        :0x20,
    'KEY_LEFT_CTRL'       :0x80,
    'KEY_LEFT_SHIFT'      :0x81,
    'KEY_LEFT_ALT'        :0x82,
    'KEY_LEFT_GUI'        :0x83,
    'KEY_RIGHT_CTRL'      :0x84,
    'KEY_RIGHT_SHIFT'     :0x85,
    'KEY_RIGHT_ALT'       :0x86,
    'KEY_RIGHT_GUI'       :0x87,
    'KEY_UP_ARROW'        :0xDA,
    'KEY_DOWN_ARROW'      :0xD9,
    'KEY_LEFT_ARROW'      :0xD8,
    'KEY_RIGHT_ARROW'     :0xD7,
    'KEY_BACKSPACE'       :0xB2,
    'KEY_TAB'             :0xB3,
    'KEY_ENTER'           :0xB0,
    'KEY_RETURN'          :0xB0,
    'KEY_ESC'             :0xB1,
    'KEY_INSERT'          :0xD1,
    'KEY_DELETE'          :0xD4,
    'KEY_PAGE_UP'         :0xD3,
    'KEY_PAGE_DOWN'       :0xD6,
    'KEY_HOME'            :0xD2,
    'KEY_END'             :0xD5,
    'KEY_CAPSLOCK'        :0xC1,
    'KEY_CAPS_LOCK'       :0xC1,
    'KEY_F1'              :0xC2,
    'KEY_F2'              :0xC3,
    'KEY_F3'              :0xC4,
    'KEY_F4'              :0xC5,
    'KEY_F5'              :0xC6,
    'KEY_F6'              :0xC7,
    'KEY_F7'              :0xC8,
    'KEY_F8'              :0xC9,
    'KEY_F9'              :0xCA,
    'KEY_F10'             :0xCB,
    'KEY_F11'             :0xCC,
    'KEY_F12'             :0xCD,
    'KEY_KEYPAD_NUMLOCK'  :0xDB,
    'KEY_KEYPAD_SLASH'    :0xDC,
    'KEY_KEYPAD_STAR'     :0xDD,
    'KEY_KEYPAD_MINUS'    :0xDE,
    'KEY_KEYPAD_PLUS'     :0xDF,
    'KEY_KEYPAD_ENTER'    :0xE0,
    'KEY_KEYPAD_1'        :0xE1,
    'KEY_KEYPAD_2'        :0xE2,
    'KEY_KEYPAD_3'        :0xE3,
    'KEY_KEYPAD_4'        :0xE4,
    'KEY_KEYPAD_5'        :0xE5,
    'KEY_KEYPAD_6'        :0xE6,
    'KEY_KEYPAD_7'        :0xE7,
    'KEY_KEYPAD_8'        :0xE8,
    'KEY_KEYPAD_9'        :0xE9,
    'KEY_KEYPAD_0'        :0xEA,
    'KEY_KEYPAD_POINT'    :0xEB,
}

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
    
def checkPort(port, i, results):
    HRPort = ''
    response = ''
    try:
        sp = serial.Serial(port = port, baudrate = 9600, bytesize = serial.EIGHTBITS, parity= serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 0.2, write_timeout = 1)
        if (sp.write('?\n') == 2):
            response = getResponse(sp, '$')
    except:
        pass
    if response.strip() == 'HotRod':
        results[i] = port
    sp.close()
    return
    
def findHotRod():
    ports = getSerialPorts()
    results = ['' for p in ports]
    threads = []
    for i, port in enumerate(ports):
        t = threading.Thread(name="port%d" % i, target=checkPort, args = (port,i,results,))
        t.setDaemon(True)
        threads.append(t)
        t.start()
        
    finished = False        
    while not finished:
        for t in threads:
            if not t.isAlive():
                finished = True
                break
    result =  [r for r in results if len(r) > 1]
    if len(result) > 0:
        return result[0]
    else:
        return None
                    
    
    
                
    
        
    
        
        
