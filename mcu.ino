#include <Servo.h>

Servo ringFinger;
Servo indexFinger;
Servo middleFinger;
Servo thumb;
Servo littleFinger;

//  Servo mechanical limits (tune) 
const int IDX_MIN = 45, IDX_MAX = 150;
const int MID_MIN = 45, MID_MAX = 150;
const int RNG_MIN = 45, RNG_MAX = 150;
const int LIT_MIN = 45, LIT_MAX = 150;
const int THM_MIN = 45, THM_MAX = 150;

//  extra pull when fully closing middle finger (try 0 first)
const int MIDDLE_CLOSE_OVERDRIVE = 0;

String line;

int clampInt(int v, int lo, int hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

bool parse5CSV(const String& s, int &a, int &b, int &c, int &d, int &e) {
  int p1 = s.indexOf(',');
  if (p1 < 0) return false;
  int p2 = s.indexOf(',', p1 + 1);
  if (p2 < 0) return false;
  int p3 = s.indexOf(',', p2 + 1);
  if (p3 < 0) return false;
  int p4 = s.indexOf(',', p3 + 1);
  if (p4 < 0) return false;

  a = s.substring(0, p1).toInt();
  b = s.substring(p1 + 1, p2).toInt();
  c = s.substring(p2 + 1, p3).toInt();
  d = s.substring(p3 + 1, p4).toInt();
  e = s.substring(p4 + 1).toInt();
  return true;
}

void applyAngles(int idx, int mid, int rng, int lit, int thm) {
  idx = clampInt(idx, IDX_MIN, IDX_MAX);
  mid = clampInt(mid, MID_MIN, MID_MAX);
  rng = clampInt(rng, RNG_MIN, RNG_MAX);
  lit = clampInt(lit, LIT_MIN, LIT_MAX);
  thm = clampInt(thm, THM_MIN, THM_MAX);

  if (mid <= (MID_MIN + 3)) {
    mid = clampInt(mid - MIDDLE_CLOSE_OVERDRIVE, 0, 180);
  }

  
  // ring=3, thumb=6, index=9, little=11, middle=12
  indexFinger.write(idx);
  middleFinger.write(mid);
  ringFinger.write(rng);
  littleFinger.write(lit);
  thumb.write(thm);
}

void setup() {
  Serial.begin(9600);

  ringFinger.attach(3);
  thumb.attach(6);
  indexFinger.attach(9);
  littleFinger.attach(11);
  middleFinger.attach(12);

  // Safe initial pose (closed-)
  applyAngles(IDX_MIN, MID_MIN, RNG_MIN, LIT_MIN, THM_MIN);
}

void loop() {
  while (Serial.available()) {
    char ch = (char)Serial.read();
    if (ch == '\n') {
      int idx, mid, rng, lit, thm;
      if (parse5CSV(line, idx, mid, rng, lit, thm)) {
        applyAngles(idx, mid, rng, lit, thm);
      }
      line = "";
    } else if (ch != '\r') {
      line += ch;
      if (line.length() > 60) line = ""; // avoid runaway
    }
  }
}