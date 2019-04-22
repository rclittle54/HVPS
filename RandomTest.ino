void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.begin(115200);
  randomSeed(analogRead(0));

}


void LEDBlip() {
  digitalWrite(LED_BUILTIN, LOW);
  delay(10);
  digitalWrite(LED_BUILTIN, HIGH);
}

long long int loopcounter = 0;
long randval;
float outval;
float temp;
float randmodifier = 0.001;
int timedelay = 50;


boolean newString = false;
String inString = "";
int num = 0;
int threshold = 10;
int printnum = 0;

float floatVal=0;

void loop() {
  // put your main code here, to run repeatedly

  if (Serial.available() > 0 && newString == false) {
    inString = Serial.readStringUntil('\n');
    floatVal = inString.toFloat();
    //Serial.println(floatVal);
    randmodifier = floatVal;
  }

  temp = loopcounter*0.05;
  //outval = floatVal + randmodifier*0.01*random(100);
  //outval = floatVal + floatVal*0.01*random(100);
  outval = floatVal + 0.25*0.01*random(100);
  //outval = random(100);
  Serial.print(outval);
  Serial.print(" ");
  Serial.println(temp);
  delay(timedelay);
  //loopcounter++;
}
