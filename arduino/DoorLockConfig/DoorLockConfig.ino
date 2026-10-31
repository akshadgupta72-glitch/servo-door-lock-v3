#include <Servo.h>
#include <IRremote.hpp>

const byte SERVO_PIN = 9;
const byte IR_PIN = 2;
const byte BUZZER_PIN = 13;

const int REST_ANGLE = 0;
const int LOCK_ANGLE = 70;

Servo doorServo;
bool isLocked = false;

const int BEEP_FREQUENCY = 1000;
const int BEEP_DURATION = 100;

void simpleBeep() {
  tone(BUZZER_PIN, BEEP_FREQUENCY,
       BEEP_DURATION);
}

void toggleLock() {
  if (!isLocked) {
    isLocked = true;

    Serial.println("LOCKING");

    simpleBeep();
    doorServo.write(LOCK_ANGLE);

  } else {
    isLocked = false;

    Serial.println("UNLOCKING");

    simpleBeep();
    doorServo.write(REST_ANGLE);
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(BUZZER_PIN, OUTPUT);

  doorServo.attach(SERVO_PIN);
  doorServo.write(REST_ANGLE);

  IrReceiver.begin(IR_PIN,
                   DISABLE_LED_FEEDBACK);

  Serial.println("Door Lock Ready");
}

void loop() {
  if (IrReceiver.decode()) {
    auto &data = IrReceiver.decodedIRData;

    if (!(data.flags &
          IRDATA_FLAGS_IS_REPEAT)) {

      Serial.print("IR Command: 0x");
      Serial.println(data.command, HEX);

      toggleLock();
    }

    IrReceiver.resume();
  }
}
