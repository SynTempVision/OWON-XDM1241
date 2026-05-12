import serial
import time

PORT = "COM3"
BAUD = 115200
NUM_READS = 5
INTERVAL = 7

MODES = {
    1:  ("DC Voltage",   b"CONFigure:VOLT:DC\n", "V",  True),
    2:  ("AC Voltage",   b"CONFigure:VOLT:AC\n", "V",  True),
    3:  ("DC Current",   b"CONFigure:CURR:DC\n", "A",  False),
    4:  ("AC Current",   b"CONFigure:CURR:AC\n", "A",  False),
    5:  ("Ohms (2-wire)",b"CONFigure:RES\n",     "Ω",  False),
    6:  ("Ohms (4-wire)",b"CONFigure:FRES\n",    "Ω",  False),
    7:  ("Capacitance",  b"CONFigure:CAP\n",     "F",  False),
    8:  ("Frequency",    b"CONFigure:FREQ\n",    "Hz", False),
    9:  ("Diode",        b"CONFigure:DIOD\n",    "V",  True),
    10: ("Continuity",   b"CONFigure:CONT\n",    "Ω",  False),
}

def format_reading(raw, unit, force_mv=False):
    try:
        v = float(raw)
    except ValueError:
        return raw
    if abs(v) >= 1e8:
        return "OL"
    if force_mv:
        return f"{v*1e3:.4f} mV"
    if abs(v) >= 1e6:
        return f"{v/1e6:.4f} M{unit}"
    if abs(v) >= 1e3:
        return f"{v/1e3:.4f} k{unit}"
    if abs(v) >= 1:
        return f"{v:.4f} {unit}"
    if abs(v) >= 1e-3:
        return f"{v*1e3:.4f} m{unit}"
    if abs(v) >= 1e-6:
        return f"{v*1e6:.4f} μ{unit}"
    return f"0.0000 {unit}"

print("=" * 40)
print("  XDM1241 Mode Reader")
print("=" * 40)
print()

for num, (name, _, _unit, _fmv) in MODES.items():
    print(f"  {num:>2}. {name}")

print()
while True:
    try:
        choice = int(input("Select mode: "))
        if choice in MODES:
            break
    except ValueError:
        pass
    print("Invalid choice.")

mode_name, mode_cmd, mode_unit, mode_force_mv = MODES[choice]

while True:
    try:
        NUM_READS = int(input("How many reads? "))
        if NUM_READS > 0:
            break
    except ValueError:
        pass
    print("Enter a positive number.")

while True:
    try:
        INTERVAL = int(input("Seconds between reads? "))
        if INTERVAL >= 0:
            break
    except ValueError:
        pass
    print("Enter 0 or more seconds.")

print(f"\nMode: {mode_name}")
print(f"Taking {NUM_READS} readings, {INTERVAL}s apart...\n")

with serial.Serial(PORT, BAUD, timeout=2) as dmm:
    dmm.write(mode_cmd)
    time.sleep(0.5)

    for i in range(1, NUM_READS + 1):
        dmm.write(b"MEAS1?\n")
        raw = dmm.readline().decode().strip()
        print(f"  [{i}/{NUM_READS}] {format_reading(raw, mode_unit, mode_force_mv)}")
        if i < NUM_READS:
            time.sleep(INTERVAL)

print("\nDone.")
