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
int buttonState = 0;  //to check the state of the button

const int soundSensorPin = 13;

uint8_t distance_read;


#define ID_SENSOR_LIGHT 1
#define ID_SENSOR_NOISE 2

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
#define INDIGO 7
#define VIOLET 8
#define NYAN_CAT 9

#define BRIGHTNESS_LOW 0
#define BRIGHTNESS_MEDIUM 1
#define BRIGHTNESS_HIGH 2

#define PIN_NEO_PIXEL 8  // Arduino pin that connects to NeoPixel
#define NUM_PIXELS 62    // The number of LEDs (pixels) on NeoPixel

Adafruit_NeoPixel strip(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

//SERIAL READ BUFFER
const int BUFFER_SIZE = 100;
byte serial_buf[BUFFER_SIZE];

int loggedState = 0;
int enteredState = 0;
int initializedRoomState = 0;

int currentColor = NO_COLOR;
int currentBrightness = BRIGHTNESS_MEDIUM;
int currentTemperature = 0;

unsigned int light_sensor_read;
unsigned int soundSensorData;

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
  pinMode(soundSensorPin, INPUT);


  strip.begin();            // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();             // Turn OFF all pixels ASAP
  strip.setBrightness(50);  // Set BRIGHTNESS to about 1/5 (max = 255)
  strip.clear();





  // Init LCD
  lcd.begin(16, 2);
  lcd.clear();

  //Init Matrix
  matrix.begin(0x70);
  matrix.clear();

  //////////////////////
}

void loop() {



  /*** RECEIVING THE MESSAGE ***/

  if (Serial.available() > 0) {
    // read the incoming bytes:
    int rlen = Serial.readBytesUntil(255, serial_buf, BUFFER_SIZE);

    // prints the received data [to see them on Realterm]
    for (int i = 0; i < rlen; i++)
      Serial.write(serial_buf[i]);


    //MATRIX CHANGE

    if (serial_buf[0] == 0) {

      if (serial_buf[1] == 0) {

        loggedState = 0;
        lcd.clear();
        lcd.print(String("logged: ") + String(loggedState));
      } else if (serial_buf[1] == 1) {
        loggedState = 1;
      } else if (serial_buf[1] == 2) {
        //faccina
      }
    }
    //     //LED COLOR CHANGE
    if (serial_buf[0] == 1) {

      currentColor = serial_buf[1];
      if(initializedRoomState ==1) changeStripColor(currentColor);
    }

    //LED BRIGHTNESS CHANGE
    if (serial_buf[0] == 2) {

      currentBrightness = serial_buf[1];
      if(initializedRoomState ==1) changeStripBrightness(currentBrightness);
    }

    //LCD CHANGE
    if (serial_buf[0] == 3) {

      currentTemperature = serial_buf[1];

      if(initializedRoomState ==1) changeTemperature(currentTemperature);
    }
  }


   /** If logged and Triggered by ultrasonic sensor = Activate room  **/


   if (loggedState == 1 && enteredState == 0) {

    setRoomWaiting();
    lcd.print("waiting");

  //   //Waiting for the user to enter the room

     Serial.print("Distance in cm: ");
     distance_read = (uint8_t)ultrasonic.distanceRead();
     Serial.println(distance_read);

     if (distance_read >= 3 && distance_read <= 10)
     {

       enteredState = 1;
     }
   }


     if (enteredState == 1 && loggedState==1 && initializedRoomState ==0) {

      activateRoom();

       initializedRoomState = 1;

     }

     if(enteredState == 1 && loggedState==1 && initializedRoomState ==1)
     {

     //** CHECK IF BUTTON IS PRESSED TO SHUT DOWN **//

     buttonState = digitalRead(buttonPin);

     // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
       if (buttonState == HIGH) {
         Serial.println("Bottone cliccato");
         enteredState = 0;
         initializedRoomState = 0;
         shutDownRoom();

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
    Serial.write(ID_SENSOR_LIGHT);
    Serial.write(2);  //data size
    Serial.write(highByte(light_sensor_read));
    Serial.write(lowByte(light_sensor_read));
    Serial.write(254);  // /xfe

    //LETTURA SENSORE RUMORE

    soundSensorData = digitalRead(soundSensorPin);

    Serial.write(255);
    Serial.write(ID_SENSOR_NOISE);
    Serial.write(1);  //data size
    Serial.write(soundSensorData);
    Serial.write(254);  // /xfe

    startMillis = currentMillis;
  }
     }



  //   //Se logout, spegni stanza

     if(loggedState == 0){
       shutDownRoom();
       enteredState = 0;
       initializedRoomState = 0;
     }

  /****************************/
}


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

void shutDownRoom() {
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
  lcd.clear();
  lcd.print("Shut down");
  matrix.clear();
  matrix.writeDisplay();
}

void setRoomWaiting() {
  //init LED strip
  changeStripColor(NO_COLOR);

  //init LCD
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("WAITING");

  //init Matrix

  matrix.setRotation(1);
  matrix.drawBitmap(0, 0, smile_bmp, 8, 8, LED_ON);
  matrix.writeDisplay();
}

void activateRoom() {
  changeTemperature(currentTemperature);
  changeStripBrightness(currentBrightness);
  changeStripColor(currentColor);
}



void rainbow(int wait) {


    strip.rainbow();
    strip.show();


}
