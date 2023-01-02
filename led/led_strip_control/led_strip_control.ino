#include <Adafruit_NeoPixel.h>
#include <LiquidCrystal.h>

#ifdef __AVR__
#include <avr/power.h>  // Required for 16 MHz Adafruit Trinket
#endif

#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"
#include <Ultrasonic.h>

Ultrasonic ultrasonic(6, 7);  //(trig, echo)

Adafruit_8x8matrix matrix = Adafruit_8x8matrix();

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

unsigned long startMillis = 0;
unsigned long currentMillis;
const unsigned long period = 5000;

const int buttonPin = 9;  
int buttonState = 0; //to check the state of the button

uint8_t distance_read;

//Office ID context:byte
#define OFFICE_ID 6

//SELF ID: In theory this should be unique for each program piloting one device. But in the final version there will be more ids, because it will be used only one mcu. context:byte
#define LED_ID 1

//Led strip state: ON/OFF context:byte
#define LED_ON 1
#define LED_OFF 0

//COLOR CODES context:byte

#define NO_COLOR 0
#define RED 1
#define ORANGE 2
#define YELLOW 3
#define GREEN 4
#define AQUA 5
#define BLUE 6
#define VIOLET 7
#define MAGENTA 8
#define NYAN_CAT 9

#define PIN_NEO_PIXEL 8  // Arduino pin that connects to NeoPixel
#define NUM_PIXELS 62    // The number of LEDs (pixels) on NeoPixel

Adafruit_NeoPixel strip(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

//SERIAL READ BUFFER
const int BUFFER_SIZE = 100;
byte serial_buf[BUFFER_SIZE];

int logged = 0;
int initialized = 0;

unsigned int light_sensor_read;

static const uint8_t PROGMEM
  smile_bmp[] = { B00111100,
                  B01000010,
                  B10100101,
                  B10000001,
                  B10100101,
                  B10011001,
                  B01000010,
                  B00111100 };


void setup() {

  Serial.begin(9600);
  pinMode(buttonPin, INPUT);

  strip.begin();            // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();             // Turn OFF all pixels ASAP
  strip.setBrightness(50);  // Set BRIGHTNESS to about 1/5 (max = 255)
  strip.clear();
  

  // Init LCD
  lcd.begin(16, 2);
  lcd.clear();
  // lcd.setCursor(0, 1);
  //lcd.print("init");

  //Init Matrix
  matrix.begin(0x70);

  matrix.clear();
  // matrix.drawBitmap(0, 0, smile_bmp, 8, 8, LED_ON);
  // matrix.writeDisplay();

  //////////////////////
}

void loop() {

  /** If logged and Triggered by ultrasonic sensor = Activate room  **/

  if (logged == 0) {

    Serial.print("Distance in cm: ");
    distance_read = (uint8_t)ultrasonic.distanceRead();
    Serial.println(distance_read);

    if (distance_read >= 3 && distance_read <= 10)
    {
      logged = 1;
      Serial.println("ROOM INIT: WELCOME!");
    }
  }


  if (logged == 1) {

    //** CHECK IF BUTTON IS PRESSED TO SHUT DOWN **//

  buttonState = digitalRead(buttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == HIGH) {
    Serial.println("CLICCATO hu");
    logged = 0;
    initialized = 0;
    strip.clear();
    strip.show();
    lcd.clear();
    matrix.clear();
    matrix.writeDisplay();

  } 

    /******* INIT ROOM *******/

    if (!initialized && logged ==1) {

      //init LED strip
      changeStripColor(RED);

      //init LCD
      lcd.setCursor(0, 1);
      lcd.print("init");

      //init Matrix

      matrix.setRotation(1);
      matrix.drawBitmap(0, 0, smile_bmp, 8, 8, LED_ON);
      matrix.writeDisplay();
      //matrix.setRotation(2);

      // initialized true now
      initialized = 1;
    }

    /******** SENSORI ***********/
    //LETTURA SENSORE LUCE

    currentMillis = millis();                   //get the current time
    if (currentMillis - startMillis >= period)  //test whether the period has elapsed
    {

      //Light Sensor Retrieve
      light_sensor_read = analogRead(A0);
      // Serial.println(light_sensor_read);

      Serial.write(255);
      Serial.write(light_sensor_read);
      Serial.write(254);  // /xfe

      //Noise Sensor Retrieve

      //...

      startMillis = currentMillis;
    }

    /****************************/


    /******* ATTUATORI ********/

    ////// TEMPERATURA

    /*** RECEIVING THE MESSAGE ***/

    if (Serial.available() > 0) {
      // read the incoming bytes:
      int rlen = Serial.readBytesUntil(255, serial_buf, BUFFER_SIZE);

      // prints the received data [to see them on Realterm]
      for (int i = 0; i < rlen; i++)
        Serial.write(serial_buf[i]);

      //LCD CHANGE
      if (serial_buf[0] == 2) {

        lcd.clear();
        lcd.setCursor(0, 1);
        lcd.print(serial_buf[1]);
      }

      //MATRIX CHANGE

      /******/

      //LED CHANGE

      switch (serial_buf[0]) {
        case NO_COLOR:
          strip.clear();
          break;
        case RED:
          changeStripColor(BLUE);
          break;
        case ORANGE:
          changeStripColor(GREEN);
          break;
        case YELLOW:
          changeStripColor(RED);
          break;
        case GREEN:
          changeStripColor(RED);
          break;
        case AQUA:
          changeStripColor(RED);
          break;
        case BLUE:
          changeStripColor(RED);
          break;
        case VIOLET:
          changeStripColor(RED);
          break;
        case MAGENTA:
          changeStripColor(RED);
          break;
        case NYAN_CAT:
          changeStripColor(RED);
          break;
      }
    }
  }
}

void changeStripColor(int color) {
  for (int i = 0; i < strip.numPixels(); i++) {  // For each pixel in strip...
    switch (color) {
      case NO_COLOR:
        strip.setPixelColor(i, strip.Color(255, 0, 0));  //  Set pixel's color (in RAM)
        break;
      case RED:
        strip.setPixelColor(i, strip.Color(255, 0, 0));
        break;
      case ORANGE:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case YELLOW:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case GREEN:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case AQUA:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case BLUE:
        strip.setPixelColor(i, strip.Color(0, 0, 255));
        break;
      case VIOLET:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case MAGENTA:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      case NYAN_CAT:
        strip.setPixelColor(i, strip.Color(0, 255, 0));
        break;
      default:
        strip.clear();
    }
  }
  strip.show();
}
