#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <Servo.h>
#include "ArduinoGraphics.h"   
#include "Arduino_LED_Matrix.h"

// Servo ringFinger;
// Servo indexFinger;
// Servo middleFinger;
// Servo thumb;
// Servo littleFinger;
ArduinoLEDMatrix matrix;
// 5x7 font, 7 rows per glyph, low 5 bits = columns (bit4 = leftmost)
const uint8_t FONT[6][7] = {
  {0b01110,0b10000,0b10000,0b10110,0b10010,0b10010,0b01110}, // G
  {0b11110,0b10001,0b10001,0b11110,0b10100,0b10010,0b10001}, // R
  {0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b11111}, // I
  {0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000}, // P
  {0b00000,0b00000,0b00000,0b01110,0b00000,0b00000,0b00000}, // -
  {0b11111,0b10000,0b10000,0b11110,0b00001,0b10001,0b01110}, // 5
};
const int GLYPHS = 6, GLYPH_W = 5, GAP = 1, LEAD = 12;
const int WIDE = LEAD + GLYPHS * (GLYPH_W + GAP);   // = 48
uint8_t wide[7][48];

int scrollPos = 0;
unsigned long lastStep = 0;
const unsigned long STEP_MS = 80;   // bigger = slower scroll

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

unsigned long lastScroll = 0;
const unsigned long SCROLL_PERIOD = 1500;

void setup() 
{
  Serial.begin(9600);

  matrix.begin();
  for (int r = 0; r < 7; r++)
    for (int c = 0; c < WIDE; c++) wide[r][c] = 0;
  int col = LEAD;
  for (int g = 0; g < GLYPHS; g++) 
  {
    for (int x = 0; x < GLYPH_W; x++)
      for (int r = 0; r < 7; r++)
        wide[r][col + x] = (FONT[g][r] >> (4 - x)) & 1;
    col += GLYPH_W + GAP;
  }
  
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

  // set the LED matrix to show the project name
  // if (millis() - lastScroll > SCROLL_PERIOD)
  // {
  //   matrix.beginDraw();
  //   matrix.textFont(Font_5x7);
  //   matrix.textScrollSpeed(80);
  //   matrix.beginText(0, 1, 0xFFFFFF);
  //   matrix.println("GRIP-5  ");
  //   matrix.endText(SCROLL_LEFT);
  //   matrix.endDraw();
  //   lastScroll = millis();
  // }
  updateMatrix();
}

void updateMatrix() 
{
  if (millis() - lastStep < STEP_MS) return;   // returns instantly most loops
  lastStep = millis();

  uint8_t frame[8][12] = {0};
  for (int c = 0; c < 12; c++) {
    int src = (scrollPos + c) % WIDE;
    for (int r = 0; r < 7; r++) frame[r][c] = wide[r][src];
  }
  matrix.renderBitmap(frame, 8, 12);
  scrollPos = (scrollPos + 1) % WIDE;
}
  