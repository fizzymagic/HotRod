/*

  HotRod.cpp
  Library to read scan codes from the HotRod game controller.
  
  ** Highly modified version of:
  
  PS2Keyboard.cpp - PS2Keyboard library
  Copyright (c) 2007 Free Software Foundation.  All right reserved.
  Written by Christian Weichel <info@32leaves.net>

  ** Mostly rewritten Paul Stoffregen <paul@pjrc.com> 2010, 2011
  ** Modified for use beginning with Arduino 13 by L. Abraham Smith, <n3bah@microcompdesign.com> * 
  ** Modified for easy interrup pin assignement on method begin(datapin,irq_pin). Cuningan <cuninganreset@gmail.com> **

  for more information you can read the original wiki in arduino.cc
  at http://www.arduino.cc/playground/Main/PS2Keyboard
  or http://www.pjrc.com/teensy/td_libs_PS2Keyboard.html

  Version 2.4 (March 2013)
  - Support Teensy 3.0, Arduino Due, Arduino Leonardo & other boards
  - French keyboard layout, David Chochoi, tchoyyfr at yahoo dot fr

  Version 2.3 (October 2011)
  - Minor bugs fixed

  Version 2.2 (August 2011)
  - Support non-US keyboards - thanks to Rainer Bruch for a German keyboard :)

  Version 2.1 (May 2011)
  - timeout to recover from misaligned input
  - compatibility with Arduino "new-extension" branch
  - TODO: send function, proposed by Scott Penrose, scooterda at me dot com

  Version 2.0 (June 2010)
  - Buffering added, many scan codes can be captured without data loss
    if your sketch is busy doing other work
  - Shift keys supported, completely rewritten scan code to ascii
  - Slow linear search replaced with fast indexed table lookups
  - Support for Teensy, Arduino Mega, and Sanguino added

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/
#include <Arduino.h>
#include "HotRod.h"

#define BUFFER_SIZE  64
#define HR_TIMEOUT   20
static volatile uint8_t buffer[BUFFER_SIZE];
static volatile uint8_t head, tail;
static uint8_t DataPin;
static uint8_t CharBuffer = 0;

// All scan codes from the HotRod, in ascending order, with keyboard equivalents
const uint8_t HotRodCodes[CODESIZE] PROGMEM = {
  0x11,  // L Button 2    KEY_LEFT_ALT
  0x12,  // L Button 4    KEY_LEFT_SHIFT
  0x14,  // L Button 1    KEY_LEFT_CTRL
  0x15,  // R Button 3    'q'
  0x16,  // 1 Player      '1'
  0x1A,  // L Button 5    'z'
  0x1B,  // R Button 2    's'
  0x1C,  // R Button 1    'a'
  0x1D,  // R Button 4    'w'
  0x1E,  // 2 Player      '2'
  0x21,  // L Button 7    0 
  0x22,  // L Button 6    'x' 
  0x23,  // R Joystick L  'd' 
  0x24,  // R Button 5    'e' 
  0x25,  // R Side Button '6' 
  0x26,  // L Side Button '5' 
  0x29,  // L Button 3    ' ' 
  0x2B,  // R Joystick D  'f'
  0x2D,  // R Joystick U  'r'
  0x34,  // R Joystick R  'g'
  0x54,  // R Button 6    '['
  0x5B,  // R Button 7    0 
  0x6B,  // L Joystick L  KEY_LEFT_ARROW 
  0x72,  // L Joystick D  KEY_DOWN_ARROW 
  0x74,  // L Joystick R  KEY_RIGHT_ARROW 
  0x75   // L Joystick U  KEY_UP_ARROW 
}; 

// Default key mapping for MAME, order is the same as for scan codes.
const uint8_t DefaultKeys[CODESIZE] PROGMEM = {
  KEY_LEFT_ALT,
  KEY_LEFT_SHIFT,
  KEY_LEFT_CTRL,
  'q',
  '1',
  'z',
  's',
  'a',
  'w',
  '2',
  0,
  'x',
  'd',
  'e',
  '6',
  '5',
  ' ',
  'f',
  'r',
  'g',
  '[',
  0,
  KEY_LEFT_ARROW,
  KEY_DOWN_ARROW,
  KEY_RIGHT_ARROW,
  KEY_UP_ARROW
};

// The ISR for the external interrupt
// Reads the data and puts the scan code into a circular buffer
void hrinterrupt(void)
{
	static uint8_t bitcount = 0;
	static uint8_t incoming = 0;
	static uint32_t prev_ms = 0;
	uint32_t now_ms;
	uint8_t n, val;

	val = digitalRead(DataPin);
	now_ms = millis();
	if (now_ms - prev_ms > HR_TIMEOUT) {
		bitcount = 0;
		incoming = 0;
	}
	prev_ms = now_ms;
	n = bitcount - 1;
	if (n <= 7) {
		incoming |= (val << n);
	}
	bitcount++;
	if (bitcount == 11) {
		uint8_t i = head + 1;
		if (i >= BUFFER_SIZE) i = 0;
		if (i != tail) {
			buffer[i] = incoming;
			head = i;
		}
		bitcount = 0;
		incoming = 0;
	}
}

// Reads the next scan code from the circular buffer
static inline uint8_t get_scan_code(void)
{
	uint8_t c, i;
	i = tail;
	if (i == head) return 0;
	i++;
	if (i >= BUFFER_SIZE) i = 0;
	c = buffer[i];
	tail = i;
	return c;
}

bool HotRod::available() {
	if (CharBuffer) return true;
	CharBuffer = get_scan_code();
	if (CharBuffer) return true;
	return false;
}

uint8_t HotRod::read() {
	uint8_t result;
   if (CharBuffer) {
      result = CharBuffer;
   }
   else if (available()) {
      result = CharBuffer;
   }
   else {
      result = 0;
   }
   CharBuffer = get_scan_code();
	return result;
}

HotRod::HotRod() {
  // nothing to do here, begin() does it all
}

void HotRod::begin(uint8_t data_pin, uint8_t irq_pin) {
  DataPin = data_pin;
  
  // initialize the pins
  pinMode(irq_pin, INPUT_PULLUP);
  pinMode(data_pin, INPUT_PULLUP);

  head = 0;
  tail = 0;
  
  attachInterrupt(digitalPinToInterrupt(irq_pin), hrinterrupt, FALLING);
}


