/**
* Source code:
* https://www.italiantechproject.it/tutorial-arduino/display-lcd
*/
#include <LiquidCrystal.h>
 
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
 
String messaggi[] = {
  "Hello world",
  "Ciao mondo",
  "Hola mundo",
  "Hallo Welt",
  "Bonjour le monde"
};
 
void setup(){
  lcd.begin(16, 2);
}
 
void loop(){
  for(int i = 0; i < 5; i++){
    lcd.clear();
    lcd.setCursor(5, 0);
    lcd.print("uwu");
    lcd.setCursor(0, 1);
    lcd.print(messaggi[i]);
    delay(1000);
  }
}