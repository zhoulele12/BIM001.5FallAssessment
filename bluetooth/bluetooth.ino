#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

float x, y, z;

int degreesX = 0;
int degreesY = 0;
int totalSits = 0;

unsigned long totalTime = 0;
unsigned long startTime = 0;
boolean sitting = true;

BLEService gyroService("19B10000-E8F2-537E-4F6C-D104768A1214"); // BLE LED Service

BLEByteCharacteristic countCharacteristic("19C20000-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWrite);
 

void setup() {

  // initialize serial and wait for serial monitor to be opened:
  Serial.begin(9600);
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  // begin initialization:

  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (true);
  }
  // set advertised local name and service UUID:
  BLE.setLocalName("Gyroscope");
  BLE.setAdvertisedService(gyroService);
  // add the characteristic to the service
  gyroService.addCharacteristic(countCharacteristic);
  // add service:
  BLE.addService(gyroService);
  // set the initial value for the characteristics:
  //countCharacteristic is used to write/read the final sit/stand count
  countCharacteristic.writeValue(0);
  // start advertising
  BLE.advertise();
  Serial.println("BLE Gyroscope");
}

void loop() {
// if the central device wrote to the characteristic,
  // listen for BLE peripherals to connect:
  BLEDevice central = BLE.central();
  
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());
//    Serial.println("Start test");
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
    }
    if(sitting && (x > .7 || x < -.7)){
      sitting = false;
      Serial.println("Stand up");
    }
    if(!sitting && (x < .55 && x > -.55)){
      sitting = true;
      totalSits++;
      Serial.println("Sat down");
      Serial.println(totalSits);
      //write total sit value to countCharacteristic
      countCharacteristic.writeValue(totalSits);
    } 
  
  delay(200);
}
