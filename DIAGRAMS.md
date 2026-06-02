# Extra Diagrams for Report (Final Mermaid Version)

---

## 1) System / Block Diagram (Architecture)

```mermaid
flowchart LR

CAM[Webcam Camera]
CV[OpenCV Capture]

MP[MediaPipe Hand Landmarker]

FE[Feature Extraction]

MAP[Mapping And Constraints]

FILT[Filtering And Control]

MODE{Mode Manager}

LIVE[Continuous Mirror Output]

GAME[RPS Game Mode]

PLAY[Macro Playback]

SER[Serial Protocol Layer]

UNO[Arduino UNO]

SRV[Five SG90 Servos]

HAND[Robotic Hand]

UI[UI Overlay Monitoring]

CAM --> CV

CV --> MP

MP --> FE

FE --> MAP

MAP --> FILT

FILT --> MODE

MODE --> LIVE
MODE --> GAME
MODE --> PLAY

LIVE --> SER
GAME --> SER
PLAY --> SER

SER --> UNO

UNO --> SRV

SRV --> HAND

MP --> UI
FILT --> UI
SER --> UI
```

---

## 2) Software State Machine

```mermaid
stateDiagram-v2

[*] --> LIVE

LIVE --> GAME : key g
GAME --> LIVE : key g

LIVE --> RECORDING : key r
GAME --> RECORDING : key r

RECORDING --> LIVE : recording finished
RECORDING --> GAME : return previous mode

LIVE --> PLAYBACK : key p
GAME --> PLAYBACK : key p

PLAYBACK --> LIVE : stop or finished

LIVE --> [*] : key q
GAME --> [*] : key q
PLAYBACK --> [*] : key q
RECORDING --> [*] : key q
```

---

## 3) Detailed Data Flow

```mermaid
flowchart TD

A[Receive Hand Landmarks]

B[Select Finger Points]

C[Compute Joint Angles]

D[Normalize To Openness]

E[Map To Servo Angles]

F[Apply Filtering]

G[Apply Deadband And Rate Limit]

H[Create CSV Message]

I[Arduino Parse]

J[Servo Write]

A --> B

B --> C

C --> D

D --> E

E --> F

F --> G

G --> H

H --> I

I --> J
```

---

## 4) RPS Game Mode Logic

```mermaid
flowchart TD

A[Game Mode Enabled]

B[Track Wrist Motion]

C[Compute Motion Score]

D{Motion Above Threshold}

E{Cooldown Finished}

F[Random Select Pose]

G[Convert Pose To Angles]

H[Send CSV Command]

A --> B

B --> C

C --> D

D -- No --> B

D -- Yes --> E

E -- No --> B

E -- Yes --> F

F --> G

G --> H

H --> B
```

---

## 5) Macro Recording And Playback

```mermaid
sequenceDiagram

participant User

participant Python

participant File

participant Arduino

participant Servo

User->>Python: Start Recording

loop Recording Period

Python->>Python: Store Time And Angles

end

Python->>File: Save Macro File

User->>Python: Start Playback

Python->>File: Load Macro

loop Playback

Python->>Python: Interpolate Angles

Python->>Arduino: Send CSV Angles

Arduino->>Servo: Update Servo Position

end

Python->>Python: Stop Playback
```

---

## 6) High Level Program Flow

```mermaid
flowchart TD

A[Start]

B[Initialize Serial And Config]

C[Initialize MediaPipe]

D[Open Camera]

E{Frame Valid}

F[Convert To RGB]

G[Run Detection]

H[Render Output]

I{Keyboard Input}

J[Toggle Game Mode]

K[Start Recording]

L[Play Macro]

M[Stop Playback]

N[Exit]

O[Cleanup Resources]

P[End]

A --> B

B --> C

C --> D

D --> E

E -- No --> D

E -- Yes --> F

F --> G

G --> H

H --> I

I -- g --> J

I -- r --> K

I -- p --> L

I -- s --> M

I -- q --> N

I -- none --> D

J --> D

K --> D

L --> D

M --> D

N --> O

O --> P
```

---

## 7) Callback Control Pipeline

```mermaid
flowchart TD

A[Receive Callback]

B{Playback Active}

C[Load Playback Angles]

D[Send Angles]

E[Record If Enabled]

Z[Return]

F{Game Mode}

G{Shake Detected}

H[Choose RPS Pose]

I[Send Fixed Angles]

J[Compute Finger Openness]

K[Map To Servo Targets]

L[Apply Smoothing]

M[Apply Rate Limit]

N[Record Angles]

A --> B

B -- Yes --> C

C --> D

D --> E

E --> Z

B -- No --> F

F -- Yes --> G

F -- No --> J

G -- No --> Z

G -- Yes --> H

H --> I

I --> Z

J --> K

K --> L

L --> M

M --> N

N --> Z
```
