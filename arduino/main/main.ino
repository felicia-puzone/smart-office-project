#include <Adafruit_NeoPixel.h>
#include <LiquidCrystal.h>

#ifdef __AVR__
#include <avr/power.h> 
#endif

#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"
#include <Ultrasonic.h>
#include "anim.h"

Ultrasonic ultrasonic(6, 7);  //(trig, echo)

Adafruit_8x8matrix matrix = Adafruit_8x8matrix();

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

#define PIN_NEO_PIXEL 8  // Arduino pin that connects to NeoPixel
#define NUM_PIXELS 62    // The number of LEDs (pixels) on NeoPixel

Adafruit_NeoPixel strip(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

/* Duty cycle management for Serial Instructions Reading */
unsigned long startMillisSensors = 0;
unsigned long currentMillisSensors;
const unsigned long periodSensors = 5000;

/* Duty cycle management for LED Matrix */
unsigned long startMillisLedMatrix = 0;
unsigned long currentMillisLedMatrix;
const unsigned long periodLedMatrix = 250;

/* Button Management */
const int buttonPin = 9;
int buttonState = 0;

/* Noise Sensor */
const int soundSensorPin = 13;

/* Ultrasonic Sensor */
uint8_t distance_read;

/* Animation frame number initialization */
int currentFrame = 0;

/* ID SENSORS */
#define ID_SENSOR_LIGHT 1
#define ID_SENSOR_NOISE 2

/* Led Strip States: ON/OFF */
#define LED_ON 1
#define LED_OFF 0

/* LED Color Codes */
#define NO_COLOR 0
#define RED 1
#define ORANGE 2
#define YELLOW 3
#define GREEN 4
#define AQUA 5
#define BLUE 6
#define INDIGO 7
#define VIOLET 8
#define NYAN_CAT 9

/* LED Brightness Codes */
#define BRIGHTNESS_LOW 0
#define BRIGHTNESS_MEDIUM 1
#define BRIGHTNESS_HIGH 2

/* SERIAL READ BUFFER */
const int BUFFER_SIZE = 100;
byte serial_buf[BUFFER_SIZE];

/* FSA Variables */
int occupiedState = 0;
int enteredState = 0;
int initializedRoomState = 0;

/* Current Actuators values variables */
int currentColor = NO_COLOR;
int currentBrightness = BRIGHTNESS_MEDIUM;
int currentTemperature = 0;

/* Sensor read values variables */
unsigned int light_sensor_read;
unsigned int soundSensorData;

void setup() {

  Serial.begin(9600);
  pinMode(buttonPin, INPUT);
  pinMode(soundSensorPin, INPUT);


  /* LED Strip Initialization */
  strip.begin();            // INITIALIZE NeoPixel strip object 
  strip.show();             // Turn OFF all pixels ASAP
  strip.setBrightness(50);  // Set BRIGHTNESS to about 1/5 (max = 255)
  strip.clear();

  /* LCD Initialization */
  lcd.begin(16, 2);
  lcd.clear();

  /* LED Matrix Initialization */
  matrix.begin(0x70);
  matrix.setRotation(1);

  matrix.clear();
}

void loop() {

  /* CHECKING FOR SERIAL MESSAGES */
  checkSerialMessage();

  /* STATE MANAGEMENT */

  /* If the user has occupied a room, wait until he passes through the distance sensor */
  if (occupiedState == 1 && enteredState == 0) {

    setRoomWaiting();

    /* Waiting for the user to enter the room */

    if (distance_read >= 3 && distance_read <= 10) {

      /* If user has crossed the door, change state */
      enteredState = 1;
    }
  }

  /* If the user has entered the room, activate it with data given by server through MQTT */
  if (enteredState == 1 && occupiedState == 1 && initializedRoomState == 0) {

    activateRoom();

    /* Change state */
    initializedRoomState = 1;
  }

  /* If the room is not occupied anymore, shut down and change other states */
  if (occupiedState == 0) {
    shutDownRoom();
    enteredState = 0;
    initializedRoomState = 0;
  }

  /* If the room has been activated, check if the button is pressed and send
  if (enteredState == 1 && occupiedState == 1 && initializedRoomState == 1) {
    /* Leggi lo stato del bottone e controlla lo stato del bottone. Se è premuto (HIGH), setta la stanza in WAITING */

    buttonState = digitalRead(buttonPin);

    if (buttonState == HIGH) {
      enteredState = 0;
      initializedRoomState = 0;
      setRoomWaiting();
    }

    /* SENSORS DATA RETRIEVAL */

    /* Light Sensor Reading */
    currentMillisSensors = millis();
    if (currentMillisSensors - startMillisSensors >= periodSensors) {

      light_sensor_read = analogRead(A0);

      Serial.write(255);
      Serial.write(ID_SENSOR_LIGHT);
      Serial.write(2);  //data size
      Serial.write(highByte(light_sensor_read));
      Serial.write(lowByte(light_sensor_read));
      Serial.write(254);  // /xfe

    /* Noise Sensor Reading */

      soundSensorData = digitalRead(soundSensorPin);

      Serial.write(255);
      Serial.write(ID_SENSOR_NOISE);
      Serial.write(1);  //data size
      Serial.write(soundSensorData);
      Serial.write(254);  // /xfe

      startMillisSensors = currentMillisSensors;
    }
  }
}

/* SERIAL INSTRUCTIONS READING FUNCTION */

int checkSerialMessage() {

  if (Serial.available() > 0) {
    /* read the incoming bytes: */
    int rlen = Serial.readBytesUntil(255, serial_buf, BUFFER_SIZE);

    /* prints the received data [to see them on Realterm] */
    for (int i = 0; i < rlen; i++)
      Serial.write(serial_buf[i]);

    /* ID byte 0: receiving login information */
    if (serial_buf[0] == 0) {

      /* DATA byte 0: room not occupied  */
      if (serial_buf[1] == 0) {
        occupiedState = 0;
      } 
      /* DATA byte 1: room occupied  */
      else if (serial_buf[1] == 1) {
        occupiedState = 1;
      } 
    }
    /* ID byte 1: LED Strip actuator COLOR change value */
    if (serial_buf[0] == 1) {

      currentColor = serial_buf[1];
      if (initializedRoomState == 1) changeStripColor(currentColor);
    }

    /* ID byte 2: LED Strip actuator BRIGHTNESS change value */
    if (serial_buf[0] == 2) {

      currentBrightness = serial_buf[1];
      if (initializedRoomState == 1) changeStripBrightness(currentBrightness);
    }

    /* ID byte 3: LCD actuator TEMPERATURE change value */
    if (serial_buf[0] == 3) {

      currentTemperature = serial_buf[1];

      if (initializedRoomState == 1) changeTemperature(currentTemperature);
    }
    return 1;
  }
  return 0;
}

/* ACTUATORS DRIVING FUNCTIONS */

void changeStripColor(int color) {
  for (int i = 0; i < strip.numPixels(); i++) {  // For each pixel in strip...
    switch (color) {
      case NO_COLOR:
        strip.clear();
        break;
      case RED:
        strip.setPixelColor(i, strip.Color(255, 0, 0));
        break;
      case ORANGE:
        strip.setPixelColor(i, strip.Color(255, 140, 0));
        break;
      case YELLOW:
        strip.setPixelColor(i, strip.Color(255, 255, 0));
        break;
      case GREEN:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case AQUA:
        strip.setPixelColor(i, strip.Color(51, 255, 204));
        break;
      case BLUE:
        strip.setPixelColor(i, strip.Color(0, 0, 255));
        break;
      case INDIGO:
        strip.setPixelColor(i, strip.Color(255, 51, 255));
        break;
      case VIOLET:
        strip.setPixelColor(i, strip.Color(76, 0, 153));
        break;
      case NYAN_CAT:
        rainbow(10);
        break;
      default:
        strip.clear();
    }
    strip.show();
  }
}

void changeStripBrightness(int brightness) {
  switch (brightness) {
    case BRIGHTNESS_LOW:
      strip.setBrightness(10);
      strip.show();
      break;
    case BRIGHTNESS_MEDIUM:
      strip.setBrightness(30);
      strip.show();
      break;
    case BRIGHTNESS_HIGH:
      strip.setBrightness(50);
      strip.show();
      break;
  }
}

void changeTemperature(int temperature) {
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print(String("Temperatura: ") + String(temperature) + String(" C°"));
}

/* ROOM STATES MANAGEMENT FUNCTIONS */

void shutDownRoom() {
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }

  strip.show();
  lcd.clear();
  lcd.print("OFF");

  matrix.clear();
  matrix.writeDisplay();
}

void setRoomWaiting() {
  changeStripColor(NO_COLOR);

  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("WAITING");

  waitingAnimationMatrix();
}

void activateRoom() {
  changeTemperature(currentTemperature);
  changeStripBrightness(currentBrightness);
  changeStripColor(currentColor);

  matrix.clear();
  matrix.drawBitmap(0, 0, smile_bmp, 8, 8, LED_ON);
  matrix.writeDisplay();
}

/* OTHER UTILITIES */

/* Set the Led strip color to RAINBOW */
void rainbow() {
  strip.rainbow();
  strip.show();
}

/* Generate the LED Matrix Animation */
void waitingAnimationMatrix() {
  currentMillisLedMatrix = millis();
  if (currentMillisLedMatrix - startMillisLedMatrix >= periodLedMatrix) {

    matrix.clear();

    switch (currentFrame) {
      case 0:
        matrix.drawBitmap(0, 0, frame_one, 8, 8, LED_ON);
        break;
      case 1:
        matrix.drawBitmap(0, 0, frame_two, 8, 8, LED_ON);
        break;
      case 2:
        matrix.drawBitmap(0, 0, frame_three, 8, 8, LED_ON);
        break;
      case 3:
        matrix.drawBitmap(0, 0, frame_four, 8, 8, LED_ON);
        break;
      case 4:
        matrix.drawBitmap(0, 0, frame_five, 8, 8, LED_ON);
        matrix.writeDisplay();
        break;
      case 5:
        matrix.drawBitmap(0, 0, frame_six, 8, 8, LED_ON);
        break;
      case 6:
        matrix.drawBitmap(0, 0, frame_seven, 8, 8, LED_ON);
        break;
      case 7:
        matrix.drawBitmap(0, 0, frame_eight, 8, 8, LED_ON);
        break;
      case 8:
        matrix.drawBitmap(0, 0, frame_nine, 8, 8, LED_ON);
        break;
    }

    matrix.writeDisplay();

    /* Animation frame updating for next iteration */
    currentFrame = (currentFrame + 1) % 8;

    /* Timer step updating */
    startMillisLedMatrix = currentMillisLedMatrix;
  }
}
