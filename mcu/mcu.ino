#include <Servo.h>

Servo ringFinger;
Servo indexFinger;
Servo middleFinger;
Servo thumb;
Servo littleFinger;

const int OPEN_ANGLE = 150;
const int CLOSED_ANGLE = 45;
const int MIDDLE_FOLD_OVERDRIVE = 25; // extra pull for middle finger

void setup() 
{
  Serial.begin(9600);

  ringFinger.attach(3);
  thumb.attach(6);
  indexFinger.attach(9);
  littleFinger.attach(11);
  middleFinger.attach(12);

  // initializing the hand to closed state
  thumb.write(CLOSED_ANGLE);
  indexFinger.write(CLOSED_ANGLE);
  middleFinger.write(CLOSED_ANGLE);
  ringFinger.write(CLOSED_ANGLE);
  littleFinger.write(CLOSED_ANGLE);
}

void loop() 
{
  if(Serial.available() >= 5)
  {
    String state = "";

    // read the 5 characters
    for (int i = 0; i < 5; i++)
    {
      state += (char) Serial.read();
    }

    // index
    if (state[0] == '1') indexFinger.write(OPEN_ANGLE);
    else indexFinger.write(CLOSED_ANGLE);

    if (state[1] == '1') middleFinger.write(OPEN_ANGLE);
    else middleFinger.write(MIDDLE_FOLD_OVERDRIVE);

    if (state[2] == '1') ringFinger.write(OPEN_ANGLE);
    else ringFinger.write(CLOSED_ANGLE);

    if (state[3] == '1') littleFinger.write(OPEN_ANGLE);
    else littleFinger.write(CLOSED_ANGLE);

    if (state[4] == '1') thumb.write(OPEN_ANGLE);
    else thumb.write(CLOSED_ANGLE);

    while (Serial.available() > 0) Serial.read();
  } 
}
  

//   #include <Servo.h>



// Servo ringFinger;

// Servo indexFinger;

// Servo middleFinger;

// Servo thumb;

// Servo littleFinger;



// int pos = 0;



// void setup()

// {

// ringFinger.attach(3);

// thumb.attach(6);

// indexFinger.attach(9);

// littleFinger.attach(11);

// middleFinger.attach(12);

// }



// void loop()

// {

// for (pos = 45; pos <= 120; pos += 1) { // goes from 0 degrees to 180 degrees

// // in steps of 1 degree

// ringFinger.write(pos);

// delay(1);

// indexFinger.write(pos);

// delay(1);

// middleFinger.write(pos);

// delay(1);

// thumb.write(pos);

// delay(1);

// littleFinger.write(pos); // tell servo to go to position in variable 'pos'

// delay(15); // waits 15ms for the servo to reach the position

// }

// for (pos = 120; pos >= 45; pos -= 1) { // goes from 180 degrees to 0 degrees

// ringFinger.write(pos);

// delay(1);

// indexFinger.write(pos);

// delay(1);

// middleFinger.write(pos);

// delay(1);

// thumb.write(pos);

// delay(1);

// littleFinger.write(pos); // tell servo to go to position in variable 'pos'

// delay(15); // waits 15ms for the servo to reach the position

// }

// }
