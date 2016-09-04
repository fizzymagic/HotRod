#include <stdlib.h>
#include <Arduino.h>
#include <HotRod.h>

#define DATA_PIN     2
#define CLOCK_PIN    3
#define EEPromKeys   0
#define EEPromMagic  CODESIZE
#define MAGIC        0xAA
#define BUFFERSIZE   64
#define END_COMMAND  '\n'

HotRod HR;
uint8_t scanCodes[CODESIZE];
uint8_t outputKeys[CODESIZE];
bool breakMode = false;

void setup() {
  Serial.begin(9600);
  loadScanCodes();
  loadOutputKeys();
  HR.begin(DATA_PIN, CLOCK_PIN);
}

void loop() {
  int i;
  uint8_t ch, k;
  // Wait for a scan code from the HotRod
  while (!HR.available()) {
    // Check to see if anything on serial port
    if (Serial.available() > 0) {
      getComms();
    }
  }
  // F0 indicates that it will be a key release
  ch = HR.read();
  if (ch == 0xF0) {
    breakMode = true;
    return;
  }
  // Find the scan code in the table
  i = findScanCode(ch);
  if (i >= 0) {
    // Output the corresponding key to the USB
    k = outputKeys[i];
    if (k != 0) {
      if (breakMode) {
        Keyboard.release(k);
        breakMode = false;
      }
      else {
        Keyboard.press(k);
      }
    }
  }
}

// This function reads the input from the serial port.
// Bytes are stored in a buffer (circular) longer than the longest command.
// No command processing is done until it sees a \n character.
void getComms(void) {
  static int offset = 0;
  static uint8_t buffer[BUFFERSIZE];
  while (Serial.available() > 0) {
    uint8_t ch = Serial.read();
    if (ch == END_COMMAND || ch == 0) {
      buffer[offset] = 0;
      offset = 0;
      processCommand(buffer);
    }
    else {
      buffer[offset++] = ch;
      if (offset >= BUFFERSIZE) {
        offset = 0;
      }
    }
  }
}

// Process the command string
void processCommand(const uint8_t *buffer) {
  uint8_t cmd = toupper(*buffer);
  uint8_t from, to;
  int key;
  switch(cmd) {
    case 'M':
      Serial.print("Map ");
      if (parseMapCommand(buffer, &from, &to)) {
        if ((key = findScanCode(from)) >= 0) {
          outputKeys[key] = to;
          Serial.print(from, HEX);
          Serial.print(" to ");
          Serial.print(to, HEX);
          Serial.print(" ");
        }
        else {
          Serial.print("unknown scan code$");
          return;
        }
      }
      else {
        Serial.print("parse error$");
        return;
      }
      break;
    case 'S':
      saveOutputKeys();
      Serial.print("Save ");
      break;
    case 'R':
      resetOutputKeys();
      Serial.print("Reset ");
      break;
    case 'L':
      loadOutputKeys();
      Serial.print("Reload ");
      break;
    case '?':
      Serial.print("HotRod$");
      return;
    case 'D':
      for (int i = 0; i < CODESIZE; i++) {
        Serial.print(i);
        Serial.print(": ");
        Serial.print(scanCodes[i], HEX);
        Serial.print(" => ");
        Serial.println(outputKeys[i], HEX);
      }
      break;
    default:
      Serial.print("Unknown command$");
      return;
  }
  Serial.print("OK$");
}

// Binary search of key codes. 
// If the result of the search is not a key code in the set, returns -1
int findScanCode(uint8_t target) {
  int iMin = 0, iMax = CODESIZE - 1, iMiddle;
  int ctr = 0;
  uint8_t c;
  while (iMin <= iMax) {
    iMiddle = (iMax + iMin) / 2;
    c = scanCodes[iMiddle];
    if (c > target) {
      iMax = iMiddle - 1;
    } else if (c < target) {
      iMin = iMiddle + 1;
    } else if (c == target) {
      iMin = iMiddle;
      break;
    }
    else if (++ctr > 6) {
      return -1;
    }
  }
  if (scanCodes[iMin] == target) {
    return iMin;
  }
  else {
    return -1;
  }
}

// Copy scan codes from PROGMEM into RAM
void loadScanCodes(void) {
  memcpy_P(scanCodes, HotRodCodes, CODESIZE);
}

// Copy output key mapping from EEPROM or PROGMEM into RAM
void loadOutputKeys(void) {
  if (eeprom_read_byte((const uint8_t *) EEPromMagic) == MAGIC) {
    eeprom_read_block(outputKeys, (const uint8_t *) EEPromKeys, CODESIZE);
  }
  else {
    memcpy_P(outputKeys, DefaultKeys, CODESIZE);
  }
}

// Reset key mappings from PROGMEM
void resetOutputKeys(void) {
  memcpy_P(outputKeys, DefaultKeys, CODESIZE);
}

// Save current key mapping to EEPROM
void saveOutputKeys(void) {
  eeprom_update_block(outputKeys, (uint8_t *) EEPromKeys, CODESIZE);
  eeprom_update_byte((uint8_t *) EEPromMagic, MAGIC);
}

// Parsing for the map command, which is the most complex.
bool parseMapCommand(const uint8_t *buffer, uint8_t *from, uint8_t *to) {
  int bufLength = strlen((char *) buffer);
  int i = 0, j = 0;
  uint8_t tmp[16], ch;
  while (buffer[i] != ' ' && i < bufLength) i++;
  while (buffer[i] == ' ' && i < bufLength) i++;
  while ((ch = buffer[i]) != ' ' && j < 16 && i < bufLength) {
    i++;
    if (ch == 0 || i >= bufLength) return false;
    else {
      tmp[j++] = ch;
    }
  }
  if (j != 2) {
    return false;
  }
  tmp[j] = 0;
  *from = strtoul((const char *) tmp, NULL, 16);
  j = 0;
  while (buffer[i] == ' ' && i < bufLength) i++;
  while ((ch = buffer[i]) != 0 && j < 16 && i < bufLength) {
    i++;
    tmp[j++] = ch;
    if (ch == 0 || i >= bufLength) break;
  }
  if (j != 2) {
    return false;
  }
  tmp[j] = 0;
  *to = strtoul((const char *) tmp, NULL, 16);
  return true;
}

