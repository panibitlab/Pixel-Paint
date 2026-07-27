import serial
import serial.tools.list_ports
import time


class ArduinoController:
    def __init__(self):
        self.arduino = None
        self.port_name = None
        self.ready = False

    def scan_and_connect(self):
        ports = serial.tools.list_ports.comports()
        available_ports = [p.device for p in ports]

        # If already connected, check if still present
        if self.arduino is not None:
            if self.port_name not in available_ports:
                try:
                    self.arduino.close()
                except:
                    pass
                self.arduino = None
                self.port_name = None
                self.ready = False
                return False
            return True

        # Try connecting to any available port
        for port in ports:
            try:
                self.ready = False

                arduino = serial.Serial(port.device, 9600, timeout=1)

                time.sleep(2)
                arduino.reset_input_buffer()
                arduino.reset_output_buffer()

                self.arduino = arduino
                self.port_name = port.device
                self.ready = True

                return True

            except serial.SerialException:
                continue

        return False

    def send_pattern(self, pattern):
        if not self.ready:
            print("Arduino not ready")
            return
        try:
            self.arduino.write(bytes(pattern))
        except serial.SerialException:
            self.ready = False


