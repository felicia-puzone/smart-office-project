/*************************************************** 
  This is a library for our I2C LED Backpacks

  Designed specifically to work with the Adafruit LED Matrix backpacks 
  ----> http://www.adafruit.com/products/872
  ----> http://www.adafruit.com/products/871
  ----> http://www.adafruit.com/products/870

  These displays use I2C to communicate, 2 pins are required to 
  interface. There are multiple selectable I2C addresses. For backpacks
  with 2 Address Select pins: 0x70, 0x71, 0x72 or 0x73. For backpacks
  with 3 Address Select pins: 0x70 thru 0x77

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"
#include "anim.h"

Adafruit_8x8matrix matrix = Adafruit_8x8matrix();

void setup() {
  Serial.begin(9600);
  Serial.println("8x8 LED Matrix Test");
  
  matrix.begin(0x70);  // pass in the address
}



void loop() {
    matrix.setRotation(1);
  matrix.clear();
  matrix.drawBitmap(0, 0, frame_one, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

  matrix.clear();
  matrix.drawBitmap(0, 0, frame_two, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

    matrix.clear();
  matrix.drawBitmap(0, 0, frame_one, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

  
  matrix.clear();
  matrix.drawBitmap(0, 0, frame_two, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

  matrix.clear();
  matrix.drawBitmap(0, 0, frame_three, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

    matrix.clear();
  matrix.drawBitmap(0, 0, frame_four, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

    matrix.clear();
  matrix.drawBitmap(0, 0, frame_five, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

    matrix.clear();
  matrix.drawBitmap(0, 0, frame_six, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

    matrix.clear();
  matrix.drawBitmap(0, 0, frame_seven, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);


      matrix.clear();
  matrix.drawBitmap(0, 0, frame_eight, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

  
      matrix.clear();
  matrix.drawBitmap(0, 0, frame_nine, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(250);

}