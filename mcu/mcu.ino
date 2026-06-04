#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <Servo.h>

// Servo ringFinger;
// Servo indexFinger;
// Servo middleFinger;
// Servo thumb;
// Servo littleFinger;

const int OPEN_ANGLE = 150;
const int CLOSED_ANGLE = 45;
const int MIDDLE_FOLD_OVERDRIVE = 25; // extra pull for middle finger

bool isWireConnected = false;
const unsigned long TIMEOUT_MS = 6000; // 6 second timeout
const int MODE_PIN = 7;

float current[5];
int target[5];

const float SMOOTH = 0.25;

Servo servos[5]; 

char buf[8];
int idx = 0;

const char* ssid = "sejong-guest";
const char* password = "0234083114";

unsigned int localPort = 4210;
char packetBuffer[32];

WiFiUDP Udp;

void setup() 
{
  Serial.begin(9600);
  
  // Mode detection: LOW = serial, HIGH = wireless
  pinMode(MODE_PIN, INPUT_PULLUP);
  delay(50);
  isWireConnected = (digitalRead(MODE_PIN) == LOW);

  Serial.println(isWireConnected ? "Mode: SERIAL" : "Mode: WIRELESS");

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

  if (!isWireConnected)
  {
    // connect to WiFi
        Serial.print("Connecting to: ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);

    unsigned long wifiStart = millis();
    while (WiFi.status() != WL_CONNECTED)
    {
      if (millis() - wifiStart > 15000)
      {
        Serial.println("WiFi failed.");
        return;
      }
      delay(500);
      Serial.print(".");
    }
    delay(1000);  // let DHCP settle
    Serial.println();
    Serial.print("Connected to IP: ");
    Serial.println(WiFi.localIP());
    Udp.begin(localPort);
    Serial.print("Listening on UDP port: ");
    Serial.println(localPort);
  }
}

void loop()              
{
  if (isWireConnected)
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
  }
  else
  {
    if (WiFi.status() == WL_CONNECTED)
    {
      // read any incoming UDP packet, feed bytes through the same parser
      int packetSize = Udp.parsePacket();
      if (packetSize)
      {
        int len = Udp.read(packetBuffer, sizeof(packetBuffer));
        for (int j = 0; j < len; j++)
        {
          char c = packetBuffer[j];
          if (c == '\n')
          {
            if (idx >= 5)
            {
              for (int i = 0; i < 5; i++)
              {
                target[i] = map(buf[i] - '0', 0, 9, CLOSED_ANGLE, OPEN_ANGLE);
              }
            }
            idx = 0;
          }
          else if (idx < (int)sizeof(buf) - 1)
          {
            buf[idx++] = c;
          }
        }
      } 
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
  