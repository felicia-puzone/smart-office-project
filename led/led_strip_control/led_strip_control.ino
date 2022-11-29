#include <Adafruit_NeoPixel.h>
#include <LiquidCrystal.h>
 
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

unsigned long startMillis = 0;
unsigned long currentMillis;
const unsigned long period = 5000;

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

#define PIN_NEO_PIXEL  6   // Arduino pin that connects to NeoPixel
#define NUM_PIXELS     62  // The number of LEDs (pixels) on NeoPixel

Adafruit_NeoPixel strip(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

//SERIAL READ BUFFER
const int BUFFER_SIZE = 100;
byte serial_buf[BUFFER_SIZE];

int status =1;

unsigned int light_sensor_read;


void setup() {

  Serial.begin(9600);
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(50); // Set BRIGHTNESS to about 1/5 (max = 255)
  lcd.begin(16, 2);
  // Init LCD
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("init");

  //////////////////////
}

void loop() {

/******** SENSORI ***********/
  //LETTURA SENSORE LUCE

  currentMillis = millis();  //get the current time
  if (currentMillis - startMillis >= period)  //test whether the period has elapsed
  {
  light_sensor_read = analogRead(A0);  

  Serial.write(255);
  Serial.write(light_sensor_read);
  Serial.write(254); // /xfe

  startMillis = currentMillis;  
}

/****************************/


/******* ATTUATORI ********/

////// TEMPERATURA

///// LED

  changeStripColor(RED);

  if(status==1)
    strip.clear();

  if (Serial.available() > 0) {
    // read the incoming bytes:
    int rlen = Serial.readBytesUntil(255, serial_buf, BUFFER_SIZE);

    if(serial_buf[0]==2){

      lcd.clear();
      lcd.setCursor(0, 1);
      lcd.print(serial_buf[1]);
    }

    // prints the received data [to see them on Realterm]
    for(int i = 0; i < rlen; i++)
      Serial.write(serial_buf[i]);

    switch (serial_buf[0]) {
    case NO_COLOR:
      strip.clear();
      status=0;
      break;
    case RED:
      changeStripColor(BLUE);
      status=0;
      break;
    case ORANGE:
      changeStripColor(GREEN);
      status=0;
      break;
          case YELLOW:
      changeStripColor(RED);
      status=0;
      break;
          case GREEN:
      changeStripColor(RED);
      status=0;
      break;
          case AQUA:
      changeStripColor(RED);
      status=0;
      break;
          case BLUE:
      changeStripColor(RED);
      status=0;
      break;
          case VIOLET:
      changeStripColor(RED);
      status=0;
      break;
          case MAGENTA:
      changeStripColor(RED);
      status=0;
      break;
          case NYAN_CAT:
      changeStripColor(RED);
      status=0;
      break;
    }
}
}

void changeStripColor(int color)
{
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
  switch (color) {
  case NO_COLOR:
    strip.setPixelColor(i, strip.Color(255,   0,   0));         //  Set pixel's color (in RAM)
    break;
  case RED:
    strip.setPixelColor(i, strip.Color(  0,   0, 255));
    break;
  case ORANGE:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case YELLOW:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case GREEN:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case AQUA:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case BLUE:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case VIOLET:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case MAGENTA:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  case NYAN_CAT:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  default:
    strip.clear();
  }
}
  strip.show();  


}

