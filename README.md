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
-- The Arduino needs a Caterina (or equivalent) bootloader in it.  The Arduino Micro and the A-Star both have this as the default.
- Arduino 1.6.9 or later IDE
- A 6-pin mini DIN connecter (aka a PS/2 keyboard connector)
- A completed circuit board with the appropriate wires from the DIN connector to the Arduino.  
  You can get a board from OSH Park
- Python 2.7.9 or later.
-- The pyserial library must be installed on the system.

## Getting Started

1. Wire the PS/2 connector to the Arduino, or populate the board.
  - The board design is in the **Hardware/** folder.
2. Copy the **HotRod/** folder into the Arduino **libraries/** folder in your Arduino user space. 
   If necessary, you may need to create the **libraries** folder.
3. Copy the **HotRodtoUSB/** folder into the Arduino user space.
4. Copy the **HotRodSetup/** folder into some other place on your computer.  It doesn't really
   matter where.
5. Compile and upload the HotRodtoUSB sketch to the Arduino.
   
## Using the HotRod-to-USB adapter


## Additional Information

### Pin setup:
    DIN-6 Pin    Arduino Pin
  
      1             D2
      3             GND
      4             +5V
      5             D3
