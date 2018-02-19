import sys, serial
import HotRod


def processCmdline(args):
    i = 0
    flags = []
    files = []
    port = ''
    while i < len(args):
        if args[i][0] == '-':
            if args[i][1] == 'p':
                i += 1
                port = args[i]
            else:
                flags.append(args[i])
        else:
            files.append(args[i])
        i += 1
    return (flags, files, port)
    

if len(sys.argv) == 0:
    print "Usage:"
    print "  SetupHotRod.py [-p portname] [-s] [-d] [-r] [cmdFile] ..."
    print "     cmdFile  Name of one or more serial commands file(s).  Not required."
    print "     -p  specify serial port, e.g. COM3 for Windows, /dev/ttyS2 for linux and Mac"
    print "         if not specified port will be autodetected"
    print "     -s  save mapping to EEPROM after processing file"
    print "     -d  dump current mapping after processing file"
    print "     -r  reset mapping to default before processing file"
    print "     -l  reinitialize mapping from EEPROM before processing file"
            
flags, files, HRPort = processCmdline(sys.argv[1:])

if len(HRPort) == 0:
    HRPort = HotRod.findHotRod()
    if not HRPort:
        print "No HotRod found."
        exit(1)
    else:
        print "HotRod found on port %s." % HRPort

lines = []
for inputFile in files:        
    with open(inputFile, 'r') as f:
        lines.extend([l.strip()for l in f.readlines() if len(l) > 1])
    
commands = []    
for l in lines:
    a = l.split()
    if len(a) == 0 or a[0][0] == '#':
        continue
    a[0] = a[0].upper()
    a[1] = a[1].upper()
    if a[0] == 'M':
        if a[1] in HotRod.HRCodes.keys():
            a[1] = "%02X" % HotRod.HRCodes[a[1]]
        elif len(a[1]) != 2:
            print "Bad code %s" % a[1]
            break
        if a[2] in HotRod.KBKeys.keys():
            a[2] = "%02X" % HotRod.KBKeys[a[2]]
        elif len(a[2]) == 1:
            a[2] = "%02X" % (ord(a[2]))
        elif len(a[2]) != 2:
            print "Bad code %s" % a[2]
            break
        cmd = ' '.join(a)
    else:
        cmd = a[0]
    commands.append(cmd)
   
if '-l' in flags:
    commands.insert(0, 'L')
if '-r' in flags:
    commands.insert(0, 'R')
if '-d' in flags:
    commands.append('D')
if '-s' in flags:
    commands.append('S')

sp = serial.Serial(port = HRPort, baudrate = 9600, bytesize = serial.EIGHTBITS, parity= serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 0.2, write_timeout = 1)
for cmd in commands:
    response = ''
    sp.write(cmd + '\n')
    c = sp.read(1)
    while c != '$' and c != 0:
        response += c
        c = sp.read()
    print response.strip()
    if response.rfind('OK') < 0:    
        print "Error processing commands"
        break
        

