unsigned long timerc;
int idstanza=1;
int statoAttuale = 0;
char codice = 0;
//stato 0 ascolto
//stato 1 messaggio errore
//stato 2 messaggio comando
void setup() {
  // put your setup code here, to run once:
  timerc=millis();
  Serial.begin(9600);
}
//#ff #id stanza # id sensore #tipo dato #lunghezza #dati... #fe
void loop() {
  int statoFuturo=0;
  if(millis()-timerc>2000 && statoAttuale==0)
  {
      //pacchetto temperatura
      Serial.write(0xFF); //header
      Serial.write(idstanza); //id stanza
      Serial.write(0); //temperatura
      Serial.write(0); //intero
      Serial.write(1); //lunghezza
      Serial.write(23); //valore 
      Serial.write(0xFE); //footer
      //pacchetto prossimità
      Serial.write(0xFF); //header
      Serial.write(idstanza); //id stanza
      Serial.write(1); //prossimità
      Serial.write(0); //intero
      Serial.write(1); //lunghezza
      Serial.write(23); //valore 
      Serial.write(0xFE); //footer
      //pacchetto luce
      Serial.write(0xFF); //header
      Serial.write(idstanza); //id stanza
      Serial.write(2); //luce
      Serial.write(0); //intero
      Serial.write(1); //lunghezza
      Serial.write(23); //valore 
      Serial.write(0xFE); //footer
      if(Serial.available()>1){
        char header=Serial.read();
        if(header==0xFF && Serial.available()>1){ //controlla se arrivato l'header e se ci sono altri pezzi
          char tipoMessaggio=Serial.read(); //ricava il tipo di messaggio
          if(tipoMessaggio=='C' && Serial.available()>1){ //ricava il comando da eseguire
            statoFuturo=1;
            codice=Serial.read();
          }else if(tipoMessaggio=='E' && Serial.available()>1){ //ricava l'errore
            statoFuturo=2;
            codice=Serial.read();
          }
          //cosa succede se non si entra in un if?
          //dovrebbe rimanere allo stato 0 e comando ha ancora valore 0
        }
      }
      timerc=millis();
  }else if(statoAttuale==1){
    //controlla il valore del comando
    //fai cose
    statoFuturo=1; //esegue il comando finchè non mettiamo una condizione
    codice=0; //reset
  }else if(statoAttuale==2){
    //controlla il codice errore
    //fai cose
    statoFuturo=2; //rimane in error finchè non mettiamo una condizione
    codice=0; //reset
  }
  statoAttuale=statoFuturo;
}
