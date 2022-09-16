// Import declarations Here
#include <Servo.h>

// Object declarations here
Servo scaleServo;

// Servo Pin Information
const int SCALE_PIN = 45;
// Servo Pos Information
const int POS_RIGHT = 64;
const int POS_CENTER = 80;
const int POS_LEFT = 97;

// Shift register pin information
const int serialData = 2;
const int shiftClock = 5;
const int latchClock = 4;

// Button pin information TOOD PLACEHOLDERS
const int mode1button = 18;
const int mode2button = 19;
const int mode3button = 20;

// Global Constants and Variables Go Here
const int NUMCOINS = 12;

// Button constant information
const int BUTTON1 = 0;
const int BUTTON2 = 1;
const int BUTTON3 = 2;

// Byte information for state of the LEDs
byte LEDVALS[3] = {0, 0, 0};

// Puzzle state information
int weighings = 0;
int finalGuess = 0;

// States for each puzzle mode (and a state when no puzzle in progress)
int state = 0;
const int WAITS = 0;  // Waits for the user to set up modes
const int MODE1 = 1;  // Mode 1: Coin exists and is Lighter
const int MODE2 = 2;  // Mode 2: Coin exists and is Unknown
const int MODE3 = 3;  // Mode 3: Coin exists and is Heavier


////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////// Communication Functions Between Python and Arduino //////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////

/*
 * Sends an integer to the python side as soon as it becomes available.
 */
void arduinoToPython(int toWrite) {
  while (true) {
    if (Serial.availableForWrite() >= 1)  {
      Serial.write(toWrite);
      return;
    }
  }
}


/*
 * Retrieves a byte of data from python side and returns it.
 */
int pythonToArduino() {
  // Wait for arduino message
  bool valuesRead = false;
  while (!valuesRead) {
    if (Serial.available() > 0) {
      int byteToRead = Serial.read();
      valuesRead = true;
      return byteToRead;
    }
  }
  return 0;
}


////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////// Helper Functions ///////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////


/*
 * Function that sets information for puzzle based on user button press, 
 * and tells user via lights which button was pressed
 */
void modeSetup(int mode) {
  // When weight of unique coin unknown, weighings = log_3(2 * numcoins + 3)
  // When weight of unique coin known,   weighings = log_3(numcoins)
  // In All Instances,    for 12 coins,  weighings = 3
  weighings = 3;
  
  // Setup based on mode parameter
  if (mode == MODE1) {
    // Uses states that the odd coin is heavier, and program knows that.
    arduinoToPython(MODE1);
    state = MODE1;
    // Blink entirety of left side twice 
    for (int i = 0; i < 2; i++) {
      setLightStates(255, 15, 0);
      delay(750);
      setLightStates(0, 0, 0);
      delay(750);
    }
  }
  else if (mode == MODE2) {
    // Uses states that the program does not know whether odd coin is heavier or lighter.
    arduinoToPython(MODE2);
    state = MODE2;
    // Blink entirety of both sides twice 
    for (int i = 0; i < 2; i++) {
      setLightStates(255, 255, 255);
      delay(750);
      setLightStates(0, 0, 0);
      delay(750);
    }
  }
  else if (mode == MODE3) {
    // Uses states that the odd coin is heavier, and program knows that.
    arduinoToPython(MODE3);
    state = MODE3;
    // Blink entirety of right side twice 
    for (int i = 0; i < 2; i++) {
      setLightStates(0, 240, 255);
      delay(750);
      setLightStates(0, 0, 0);
      delay(750);
    }
  }
  else {
    // This code should never run.
    return;
  }
  return;
}


/*
 * Set state of 24 LED lights based on the 3 input bytes.
 */
void setLightStates(int value1, int value2, int value3) {
  digitalWrite(latchClock, LOW); // latch
  shiftOut(serialData, shiftClock, MSBFIRST, value3); // serial data “output”, low level first
  shiftOut(serialData, shiftClock, MSBFIRST, value2); // serial data “output”, low level first
  shiftOut(serialData, shiftClock, MSBFIRST, value1); // serial data “output”, low level first
  digitalWrite(latchClock, HIGH); // latch
  return;
}


/*
 * Waits for the user to press one of the three buttons, 
 * and returns the button that was pressed.
 */
int getUserButton() {
  bool buttonPressed = false;
  while (!buttonPressed) {
    if (digitalRead(mode1button) == 0) return BUTTON1;
    else if (digitalRead(mode2button) == 0) return BUTTON2;
    else if (digitalRead(mode3button) == 0) return BUTTON3;
  }
}


////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// Main State Functions /////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////


/*
 * Determine whether each button has been read, and then
 * perform state changes and string setup, if applicable
 * 
 */
void wait() {
  if (digitalRead(mode1button) == 0) modeSetup(MODE1);
  else if (digitalRead(mode2button) == 0) modeSetup(MODE2);
  else if (digitalRead(mode3button) == 0) modeSetup(MODE3);
  return;
}


/*
 * Runs the puzzle as specified by the user. 
 * Continues until puzzle is deemed over.
 */
void runPuzzle() {
  while (state != WAITS) {
    // Turn off the lights and delay
    setLightStates(0, 0, 0);
    delay(1000);
    
    // Move servo back to resting positio
    scaleServo.write(POS_CENTER);
    delay(1000);
    
    // Retrieve weighings left from python
    weighings = pythonToArduino();

    // If no weighings left, puzzle ends
    if (weighings == 0) {
      // Retrieve final results from python
      for (int i = 2; i >= 0; i--) {
        LEDVALS[i] = pythonToArduino();
      }
      // Blink results
      for (int i = 0; i < 4; i++) {
        setLightStates(LEDVALS[0], LEDVALS[1], LEDVALS[2]);
        delay(1000);
        setLightStates(0, 0, 0);
        delay(1000);
      }
      // End the puzzle
      state = WAITS;
      return;
    }
    else {
      // Set Light States According to input
      for (int i = 2; i >= 0; i--) {
        LEDVALS[i] = pythonToArduino();
      }
      setLightStates(LEDVALS[0], LEDVALS[1], LEDVALS[2]);

      // Make user press one of the buttons
      int buttonPressed = getUserButton();

      setLightStates(0, 0, 0);

      // Move servo and delay based on button press
      if (buttonPressed == 0) scaleServo.write(POS_LEFT);
      else if (buttonPressed == 2) scaleServo.write(POS_RIGHT);
      delay(1000);
       
      // Send button pressed to the python side
      arduinoToPython(buttonPressed);
    }
  }
  // Set state to WAITS and return
  state = WAITS;
  return;
}


////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////// Setup and Main Loop Code ///////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////


/*
 * Setup Code
 * 
 */
void setup() {
  // Serial Setup (also for arduino python connection)
  Serial.begin(9600);
  Serial.print('A');
    
  // Setup and Position the  Servo 
  scaleServo.attach(SCALE_PIN);
  scaleServo.write(POS_CENTER);
  
  // Shift register pin setup
  pinMode(serialData, OUTPUT);
  pinMode(shiftClock, OUTPUT);
  pinMode(latchClock, OUTPUT);

  // Button pin setup
  pinMode(mode1button, INPUT);
  pinMode(mode2button, INPUT);
  pinMode(mode3button, INPUT);
  
  // Initializations
  setLightStates(0, 0, 0);
  state = WAITS;
  weighings = 3;
}


/*
 * Final Project Main Loop
 * 
 */
void loop() {
  // Loop code
  if (state == WAITS) wait();
  else if (state == MODE1) runPuzzle(); // Run puzzle (unique coin weight lighter)
  else if (state == MODE2) runPuzzle(); // Run puzzle (unique coin weight unknown)
  else if (state == MODE3) runPuzzle(); // Run puzzle (unique coin weight heavier)
}
