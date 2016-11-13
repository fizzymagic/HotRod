# HotRod
HotRod game controller adapter to USB

## Introduction

This project allows use of a HotRod SE controller with a modern computer.  It also adds considerable 
flexibility, allowing you to remap the HotRod controls to any keys on the keyboard with *no* driver 
configuration on your PC.  Since the device emulates a USB HID keyboard, it will work with any OS that
can use the keyboard, including Windows, Mac OS, and Linux.

## Requirements

Getting the entire thing working requires:

- 32u4-based arduino clone.  I recommand the Pololu A-Star series, but it should work with any 32u4-based board.
  - The Arduino needs a Caterina (or equivalent) bootloader in it.  The Arduino Micro and the A-Star both have this as the default.
- Arduino 1.6.9 or later IDE
- A 6-pin female mini DIN connecter (aka a PS/2 keyboard connector)
- A completed circuit board with the appropriate wires from the DIN connector to the Arduino.  
  You can get a board from OSH Park
- Python 2.7.9 or later.
  - The pyserial library must be installed on the system.

## Getting Started

1. Wire the PS/2 connector to the Arduino, or populate the board.
  - The board design is in the **Hardware/** folder.
  - The board can be obtained from OSH Park [here](https://oshpark.com/shared_projects/7dNfPtaw) 
2. Copy the **HotRod/** folder into the Arduino **libraries/** folder in your Arduino user space. 
   If necessary, you may need to create the **libraries** folder.
3. Copy the **HotRodtoUSB/** folder into the Arduino user space.
4. Copy the **HotRodSetup/** folder into some other place on your computer.  It doesn't really
   matter where.
5. Compile and upload the HotRodtoUSB sketch to the Arduino.
   
## Using the HotRod-to-USB adapter

## Using SetupHotRod.py

This Python script will automatically send commands to the HotRod interface from a file.  You can
save various configurations in command files to quickly load new controller configurations.

You will need Python 2.7.9 or later, with the ```pyserial``` library installed.

### Command Line

<pre>python SetupHotRod.py [-p portname] [-s] [-d] [-r] [cmdFile] ...
         cmdFile  Name of one or more serial commands file(s).  Not required.
         -p  specify serial port, e.g. COM3 for Windows, /dev/ttyS2 for linux and Mac
             if not specified port will be autodetected
         -s  save mapping to EEPROM after processing file
         -d  dump current mapping after processing file
         -r  reset mapping to default before processing file
         -l  reinitialize mapping from EEPROM before processing file</pre>


### Serial Command Set

The following commands are available to be sent to the HotRod interface from SetupHotRod.py; the input file
should consist of one command per line.

- **M sc kb**: Map scan code *sc* to  keyboard key *kb*
  - The scan code and keyboard key can be specified in ways:
    1. As a macro (all macros are defined in HotRod.py)
    2. As a 2-digit hexadecimal number
  - Additionally, the keyboard key can be specified:
    3. As an ASCII character
- **S**: Save the current key mapping to EEPROM
- **R**: Reset the key mapping to the original (in PROGMEM)
- **L**: Load a key mapping from EEPROM
- **D**: Dump the current key mapping
- **?**: Echo "HotRod" to serial port

### Examples:

```M HR_LEFT_JOYSTICK_UP KB_UP_ARROW```  
Maps the left joystick up to the keyboard up arrow.

```M 75 DA```  
Also maps the left joystick up to the keyboard up arrow.

```M HR_LEFT_JOYSTICK_UP i```  
Maps the left joystick up to ASCII 'i'

## Additional Information

### Pin setup:

```
DIN-6 Pin    Arduino Pin
   1             D2
   3             GND
   4             +5V
   5             D3
```
