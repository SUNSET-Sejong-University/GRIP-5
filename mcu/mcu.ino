#include <Servo.h>

// Servo ringFinger;
// Servo indexFinger;
// Servo middleFinger;
// Servo thumb;
// Servo littleFinger;

const int OPEN_ANGLE = 150;
const int CLOSED_ANGLE = 45;
const int MIDDLE_FOLD_OVERDRIVE = 25; // extra pull for middle finger

float current[5];
int target[5];

const float SMOOTH = 0.25;

Servo servos[5]; 

char buf[8];
int idx = 0;

void setup() 
{
  Serial.begin(9600);

  servos[2].attach(3);
  servos[4].attach(6);
  servos[0].attach(9);
  servos[3].attach(11);
  servos[1].attach(12);

  // initializing the hand to closed state
  for (int i = 0; i < 5; i++)
  {
    current[i] = CLOSED_ANGLE;
    target[i] = CLOSED_ANGLE;
    servos[i].write(CLOSED_ANGLE);
  }
}

void loop() 
{
  while (Serial.available() > 0)
  {
    char c = Serial.read();
    if (c == '\n')
    {
      if (idx >= 5)
      {
        for (int i = 0; i < 5; i++)
        {
          target[i] = map(buf[i] - '0', 0, 9, CLOSED_ANGLE, OPEN_ANGLE);
        }
      }
      idx = 0;                            // al;ways reset on a new line
    }
    else if (idx < (int)sizeof(buf) - 1)
    {
      buf[idx++] = c;                     // store digits (else block of the newline check)
    }
  }

  // Easing towards target every loop, regardless of serial
  for (int i = 0; i < 5; i++)
  {
    current[i] += (target[i] - current[i]) * SMOOTH;
    servos[i].write(current[i]);
  }
  delay(15);
}
  