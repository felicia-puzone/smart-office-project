#include <Ultrasonic.h>

Ultrasonic ultrasonic(6, 7); //(trig, echo)

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.print("Distance in cm: ");
  Serial.println((uint8_t)ultrasonic.distanceRead());
  delay(1000);
}