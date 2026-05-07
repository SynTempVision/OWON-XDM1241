import serial

PORT = "COM3"
BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=2) as dmm:
    dmm.write(b"*IDN?\n")
    idn = dmm.readline().decode().strip()
    print("Device:", idn)

    dmm.write(b"MEAS1?\n")
    result = dmm.readline().decode().strip()
    print("Measurement:", result)
