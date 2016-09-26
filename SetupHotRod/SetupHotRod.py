import sys, serial
import HotRod

flags = [f for f in sys.argv[1:] if f[0] == '-']
files = [f for f in sys.argv[1:] if f[0] != '-']
inputFile = files[0]

HRPort = HotRod.findHotRod()
if not HRPort:
    print "No HotRod found."
    exit(1)
else:
    print "HotRod found on port %s." % HRPort
   
with open(inputFile, 'r') as f:
    lines = [l.strip()for l in f.readlines() if len(l) > 1]
    
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
        

