#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

//Office ID context:byte
#define OFFICE_ID 6

//SELF ID: In theory this should be unique for each program piloting one device. But in the final version there will be more ids, because it will be used only one mcu. context:byte
#define LED_ID 1

//Led strip state: ON/OFF context:byte
#define LED_ON 1
#define LED_OFF 0

//COLOR CODES context:byte
#define RED 1
#define ORANGE 2
#define YELLOW 3
#define GREEN 4
#define BLUE 5
#define VIOLET 6
#define MAGENTA 7

//BLINKING MODE context:byte
#define PLAIN 1
#define BLINKING 2


#define PIN_NEO_PIXEL  6   // Arduino pin that connects to NeoPixel
#define NUM_PIXELS     62  // The number of LEDs (pixels) on NeoPixel

Adafruit_NeoPixel strip(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

//SERIAL READ BUFFER
const int BUFFER_SIZE = 100;
byte serial_buf[BUFFER_SIZE];

int status =1;


void setup() {

  Serial.begin(9600);
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(50); // Set BRIGHTNESS to about 1/5 (max = 255)
  
}

void loop() {

        changeStripColor(GREEN);

  //Serial.write(4);

  if(status==1)
    strip.clear();

  if (Serial.available() > 0) {
    // read the incoming bytes:
    int rlen = Serial.readBytesUntil(255, serial_buf, BUFFER_SIZE);

    // prints the received data [to see them on Realterm]
    for(int i = 0; i < rlen; i++)
      Serial.write(serial_buf[i]);

    switch (serial_buf[0]) {
    case RED:
      changeStripColor(RED);
      status=0;
      break;
    case BLUE:
      changeStripColor(BLUE);
      status=0;
      break;
    case GREEN:
      changeStripColor(GREEN);
      status=0;
      break;
    }
}
}

void changeStripColor(int color)
{
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
  switch (color) {
  case RED:
    strip.setPixelColor(i, strip.Color(255,   0,   0));         //  Set pixel's color (in RAM)
    break;
  case BLUE:
    strip.setPixelColor(i, strip.Color(  0,   0, 255));
    break;
  case GREEN:
    strip.setPixelColor(i, strip.Color(  0,   255, 0));
    break;
  default:
    strip.clear();
  }
}
  strip.show();  
}

