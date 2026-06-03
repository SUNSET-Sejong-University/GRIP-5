#include <Servo.h>

// Servo ringFinger;
// Servo indexFinger;
// Servo middleFinger;
// Servo thumb;
// Servo littleFinger;

const int OPEN_ANGLE = 150;
const int CLOSED_ANGLE = 45;
const int MIDDLE_FOLD_OVERDRIVE = 25; // extra pull for middle finger

int target[5], current[5];
Servo servos[5]; 

void setup() 
{
  Serial.begin(9600);

  servos[2].attach(3);
  servos[4].attach(6);
  servos[0].attach(9);
  servos[3].attach(11);
  servos[1].attach(12);

  // initializing the hand to closed state
  servos[4].write(CLOSED_ANGLE);
  servos[0].write(CLOSED_ANGLE);
  servos[1].write(CLOSED_ANGLE);
  servos[2].write(CLOSED_ANGLE);
  servos[3].write(CLOSED_ANGLE);
}

void loop() 
{
  if(Serial.available() >= 5)
  {
    String s = Serial.readStringUntil('\n');

    // read the 5 characters
    for (int i = 0; i < 5; i++)
    {
      target[i] = map(s[i] - '0', 0, 9, CLOSED_ANGLE, OPEN_ANGLE); // digit -> servo angle
    }
    for (int i = 0; i < 5; i++)
    {
      if (current[i] < target[i]) current[i]++;
      else if (current[i] > target[i]); current[i]--;
      servos[i].write(current[i]);
    }
    delay(15);

    // // index
    // if (state[0] == '1') indexFinger.write(OPEN_ANGLE);
    // else indexFinger.write(CLOSED_ANGLE);

    // if (state[1] == '1') middleFinger.write(OPEN_ANGLE);
    // else middleFinger.write(MIDDLE_FOLD_OVERDRIVE);

    // if (state[2] == '1') ringFinger.write(OPEN_ANGLE);
    // else ringFinger.write(CLOSED_ANGLE);

    // if (state[3] == '1') littleFinger.write(OPEN_ANGLE);
    // else littleFinger.write(CLOSED_ANGLE);

    // if (state[4] == '1') thumb.write(OPEN_ANGLE);
    // else thumb.write(CLOSED_ANGLE);

    while (Serial.available() > 0) Serial.read();
  } 
}
  