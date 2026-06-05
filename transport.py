import time
import serial
import socket

class Transport:
    """Common interface: every transport exposes send(state) and close()"""
    def send(self, state):
        raise NotImplementedError
    def close(self):
        pass

class SerialTransport(Transport):
    def __init__(self, port="/dev/ttyACM0", baud=9600):
        self.ser = serial.Serial(port, baud)
        # pulse DTR to reset the board, then wait for setup() to finish
        self.ser.setDTR(False)
        time.sleep(0.1)
        self.ser.setDTR(True)
        time.sleep(2)
        self._last_sent = None

    def send(self, state):
        # send only on change - serial is reliable
        if state != self._last_sent:
            self.ser.write((state + '\n').encode())
            print(f"Sending to MCU: {state}")
            self._last_sent = state
    
    def close(self):
        self.ser.close()

class UDPTransport(Transport):
    def __init__(self, ip, port):
        self.addr = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, state):
        # send every frame - UDP can drop packets, so resending is self healing
        self.sock.sendto((state + '\n').encode(), self.addr)
        print(f"Sending to MCU: {state}")

    def close(self):
        self.sock.close()

def make_transport(mode, ip=None, port=None, serial_port='/dev/ttyACM0'):
    """pick the transport from the --mode string"""
    if mode == "serial":
        return SerialTransport(port=serial_port)
    elif mode =="wireless":
        return UDPTransport(ip, port)
    raise ValueError(f"Unknown mode: {mode}")