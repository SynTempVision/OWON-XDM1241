import serial
import time
import tkinter as tk
from tkinter import filedialog
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf import teletype

PORT = "COM3"
BAUD = 115200

STEPS = {
    1: {"name": "2.2 - Heat Up mV",             "mode_cmd": b"CONFigure:VOLT:DC\n", "sn_col": 2, "cols": [3, 4], "labels": ["Ambient mV", "Heat up mV"], "start_row": 24},
    2: {"name": "3.2 - Ohms Before Pressure",   "mode_cmd": b"CONFigure:RES\n",     "sn_col": 2, "cols": [3, 4], "labels": ["+1/-1", "+1/Ground"],       "start_row": 54},
    3: {"name": "5.2 - Ohms After Pressure",    "mode_cmd": b"CONFigure:RES\n",     "sn_col": 2, "cols": [3, 4], "labels": ["+1/-1", "+1/Ground"],       "start_row": 86},
    4: {"name": "6.2 - Ohms After Epoxy",       "mode_cmd": b"CONFigure:RES\n",     "sn_col": 2, "cols": [3, 4], "labels": ["+1/-1", "+1/Ground"],       "start_row": 102},
    5: {"name": "7.3 - Ohms After Head Install","mode_cmd": b"CONFigure:RES\n",     "sn_col": 2, "cols": [3, 4], "labels": ["+1/-1", "+1/Ground"],       "start_row": 132},
}

def iter_rows(sheet):
    for row in sheet.getElementsByType(TableRow):
        repeat = int(row.getAttribute("numberrowsrepeated") or 1)
        for _ in range(repeat):
            yield row

def iter_cells(row):
    for cell in row.getElementsByType(TableCell):
        repeat = int(cell.getAttribute("numbercolumnsrepeated") or 1)
        for _ in range(repeat):
            yield cell

def get_cell_value(sheet, target_row, target_col):
    for r_idx, row in enumerate(iter_rows(sheet), start=1):
        if r_idx == target_row:
            for c_idx, cell in enumerate(iter_cells(row), start=1):
                if c_idx == target_col:
                    parts = [teletype.extractText(p) for p in cell.getElementsByType(P)]
                    return " ".join(parts).strip()
    return ""

def set_cell_value(sheet, target_row, target_col, value):
    for r_idx, row in enumerate(iter_rows(sheet), start=1):
        if r_idx == target_row:
            for c_idx, cell in enumerate(iter_cells(row), start=1):
                if c_idx == target_col:
                    for child in list(cell.childNodes):
                        cell.removeChild(child)
                    cell.addElement(P(text=str(value)))
                    return

def countdown(prepare_seconds, measure_seconds, label):
    for i in range(prepare_seconds, 0, -1):
        print(f"\r  [{label}] Get probes in position — {i}s...  ", end="", flush=True)
        time.sleep(1)
    for i in range(measure_seconds, 0, -1):
        print(f"\r  [{label}] Measuring in {i}s...              ", end="", flush=True)
        time.sleep(1)
    print(f"\r  [{label}] Reading...                            ", end="", flush=True)

def read_meter(dmm):
    dmm.write(b"MEAS1?\n")
    return dmm.readline().decode().strip()

def pick_file():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select ITP file",
        filetypes=[("ODS files", "*.ods")]
    )
    root.destroy()
    return path

def main():
    print("=" * 50)
    print("  XDM1241 ITP Recording Tool")
    print("=" * 50)

    # Pick file
    print("\nSelect the ITP file...")
    path = pick_file()
    if not path:
        print("No file selected. Exiting.")
        return
    print(f"Loaded: {path}")

    # Pick test step
    print("\nSelect test step:")
    for num, step in STEPS.items():
        print(f"  {num}. {step['name']}")
    while True:
        try:
            choice = int(input("\nEnter number: "))
            if choice in STEPS:
                break
        except ValueError:
            pass
        print("Invalid choice.")
    step = STEPS[choice]
    print(f"\nRunning: {step['name']}")

    # Load ODS
    doc = load(path)
    sheet = next(s for s in doc.spreadsheet.getElementsByType(Table)
                 if s.getAttribute("name") == "New_Format")

    # Read TC SNs
    tcs = []
    for i in range(10):
        sn = get_cell_value(sheet, step["start_row"] + i, step["sn_col"])
        if sn:
            tcs.append((step["start_row"] + i, sn))

    if not tcs:
        print("No TC serial numbers found in this section. Exiting.")
        return

    print(f"\nFound {len(tcs)} TCs: {', '.join(sn for _, sn in tcs)}")
    input("Press Enter to begin...\n")

    # Connect to meter
    with serial.Serial(PORT, BAUD, timeout=2) as dmm:
        print(f"Connected to {PORT}")
        dmm.write(step["mode_cmd"])
        time.sleep(0.5)
        print(f"Meter mode set.\n")

        for row, sn in tcs:
            print("-" * 40)
            print(f"TC SN: {sn}")

            readings = []
            for label, col in zip(step["labels"], step["cols"]):
                input(f"  Connect probes for [{label}] — press Enter when ready")
                countdown(5, 5, label)
                value = read_meter(dmm)
                print(f"\n  {label}: {value}")
                readings.append((col, value))

            # Write to ODS
            for col, value in readings:
                set_cell_value(sheet, row, col, value)

            input("\n  Press Enter for next TC...")
            print()

    # Save
    doc.save(path)
    print("=" * 50)
    print(f"Done. Results saved to {path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
