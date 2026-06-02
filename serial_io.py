# serial_io.py
import serial

class SerialSender:
    """
    Sends angles to Arduino in CSV format: idx,mid,ring,little,thumb\\n
    """
    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud)

    def send_angles(self, angles):
        msg = f"{int(angles[0])},{int(angles[1])},{int(angles[2])},{int(angles[3])},{int(angles[4])}\n"
        self.ser.write(msg.encode("ascii"))