# **Circuit Documentation**

## **Summary**

This circuit is designed to control five Servo SG90 motors using an Arduino UNO microcontroller. The power for the servos is supplied through a Step Down Buck Converter, which is powered by a 9V Battery. The Arduino UNO is responsible for sending control signals to each servo motor, allowing for precise movement control.

## **Component List**

1. **Arduino UNO**  
   * **Description**: A microcontroller board based on the ATmega328P. It has 14 digital input/output pins, 6 analog inputs, and is programmable with the Arduino IDE.  
   * **Pins**: UNUSED, IOREF, Reset, 3.3V, 5V, GND, Vin, A0, A1, A2, A3, A4, A5, SCL, SDA, AREF, D13, D12, D11, D10, D9, D8, D7, D6, D5, D4, D3, D2, D1, D0  
2. **Servo SG90 (x5)**  
   * **Description**: A small and lightweight servo motor with high output power. It is suitable for small-scale robotics and control applications.  
   * **Pins**: Signal, Vin, Gnd  
3. **Step Down Buck Converter**  
   * **Description**: A DC-DC converter that steps down voltage from a higher level to a lower level, providing a stable output voltage.  
   * **Pins**: UOUT+, UOUT-, UIN+, UIN-  
4. **9V Battery**  
   * **Description**: A standard 9V battery used to power the circuit.  
   * **Pins**: Positive, Negative

## **Wiring Details**

### **Arduino UNO**

* **5V Pin**: Connected to UOUT+ of the Step Down Buck Converter and Vin of all Servo SG90 motors.  
* **GND Pin**: Connected to UOUT- of the Step Down Buck Converter and Gnd of all Servo SG90 motors.  
* **D3 Pin**: Connected to Signal pin of Servo SG90 (1).  
* **D6 Pin**: Connected to Signal pin of Servo SG90 (2).  
* **D9 Pin**: Connected to Signal pin of Servo SG90 (3).  
* **D11 Pin**: Connected to Signal pin of Servo SG90 (4).  
* **D12 Pin**: Connected to Signal pin of Servo SG90 (5).

### **Servo SG90 (1)**

* **Signal Pin**: Connected to D3 of the Arduino UNO.  
* **Vin Pin**: Connected to UOUT+ of the Step Down Buck Converter.  
* **Gnd Pin**: Connected to UOUT- of the Step Down Buck Converter.

### **Servo SG90 (2)**

* **Signal Pin**: Connected to D6 of the Arduino UNO.  
* **Vin Pin**: Connected to UOUT+ of the Step Down Buck Converter.  
* **Gnd Pin**: Connected to UOUT- of the Step Down Buck Converter.

### **Servo SG90 (3)**

* **Signal Pin**: Connected to D9 of the Arduino UNO.  
* **Vin Pin**: Connected to UOUT+ of the Step Down Buck Converter.  
* **Gnd Pin**: Connected to UOUT- of the Step Down Buck Converter.

### **Servo SG90 (4)**

* **Signal Pin**: Connected to D11 of the Arduino UNO.  
* **Vin Pin**: Connected to UOUT+ of the Step Down Buck Converter.  
* **Gnd Pin**: Connected to UOUT- of the Step Down Buck Converter.

### **Servo SG90 (5)**

* **Signal Pin**: Connected to D12 of the Arduino UNO.  
* **Vin Pin**: Connected to UOUT+ of the Step Down Buck Converter.  
* **Gnd Pin**: Connected to UOUT- of the Step Down Buck Converter.

### **Step Down Buck Converter**

* **UOUT+ Pin**: Connected to 5V of the Arduino UNO and Vin of all Servo SG90 motors.  
* **UOUT- Pin**: Connected to GND of the Arduino UNO and Gnd of all Servo SG90 motors.  
* **UIN+ Pin**: Connected to Positive of the 9V Battery.  
* **UIN- Pin**: Connected to Negative of the 9V Battery.

### **9V Battery**

* **Positive Pin**: Connected to UIN+ of the Step Down Buck Converter.  
* **Negative Pin**: Connected to UIN- of the Step Down Buck Converter.

(The battery is just for demonstrative purposes. The original project utilizes a 7.4V battery)