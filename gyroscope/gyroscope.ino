int xpin = A0;
int ypin = A1;
int zpin = A2;
int xval;
int yval;
int zval;
int samplesize = 10;
int count = 0;
boolean sitting = true;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  xval = analogRead(xpin);
  int x = map(xval, 245, 399, -100, 100);
  float xfinal = (float)x / (100.00);
    Serial.print("x:");
    Serial.print(xfinal);
  //  Serial.print(xval);
    Serial.print("g ");

  yval = analogRead(ypin);
  int y = map(yval, 240, 399, -100, 100);
  float yfinal = (float)y / (100.00);
    Serial.print("y:");
  Serial.print(yfinal);
  //  Serial.print(yval);
    Serial.print("g ");

  zval = analogRead(zpin);
  int z = map(zval, 240, 399, -100, 100);
  float zfinal = (float)z / (100.00);
    Serial.print("z:");
    Serial.print(zfinal);
  //  Serial.print(zval);
    Serial.println("g ");

  if (sitting && yfinal < -0.7 && zfinal < 0.2) {
    sitting = false;
    Serial.println("stood up ");

    //      Serial.print(count);
  }
  if (sitting == false && yfinal > -0.3 && zfinal > 0.85) {
    sitting = true;
    Serial.println("sat down");
    count += 1;
    Serial.print("count:");
    Serial.println(count);
  }
  delay(500);
}
