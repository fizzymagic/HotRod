# HotRod
HotRod game controller adapter to USB

** Requires a Atmel 32U4-based Arduino/clone with the Cassandra bootloader.
I personally recommend the Polulu A-Star series microcontrollers for this.

# HotRod/
Load this folder into your libraries folder in your Arduino projects folder.

# HotRodtoUSB/
Load this folder into your projects folder.

# SetupHotRod/
This folder can be located elsewhere.  It contains Python scripts to configure the interface.

# Pin setup:
    DIN-6 Pin    Arduino Pin
  
      1             D2
      3             GND
      4             +5V
      5             D3
