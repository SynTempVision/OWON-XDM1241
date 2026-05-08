from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf import teletype
import copy

ODS_PATH = r"C:\Users\synte\Downloads\ITP.0002_1ElementStandard_Rev0.ods"
OUT_PATH = r"C:\Users\synte\Downloads\ITP_TEST_OUTPUT.ods"

doc = load(ODS_PATH)
sheet = next(s for s in doc.spreadsheet.getElementsByType(Table)
             if s.getAttribute("name") == "New_Format")

def iter_rows(sheet):
    """Yield rows, expanding repeated rows."""
    for row in sheet.getElementsByType(TableRow):
        repeat = int(row.getAttribute("numberrowsrepeated") or 1)
        for _ in range(repeat):
            yield row

def iter_cells(row):
    """Yield cells, expanding repeated columns."""
    for cell in row.getElementsByType(TableCell):
        repeat = int(cell.getAttribute("numbercolumnsrepeated") or 1)
        for _ in range(repeat):
            yield cell

def get_cell(sheet, target_row, target_col):
    """Get cell at 1-based row/col."""
    for r_idx, row in enumerate(iter_rows(sheet), start=1):
        if r_idx == target_row:
            for c_idx, cell in enumerate(iter_cells(row), start=1):
                if c_idx == target_col:
                    return cell
    return None

def get_cell_value(cell):
    parts = []
    for p in cell.getElementsByType(P):
        parts.append(teletype.extractText(p))
    return " ".join(parts).strip()

def set_cell_value(sheet, target_row, target_col, value):
    """Write a string value into a cell."""
    for r_idx, row in enumerate(iter_rows(sheet), start=1):
        if r_idx == target_row:
            for c_idx, cell in enumerate(iter_cells(row), start=1):
                if c_idx == target_col:
                    # Clear existing content
                    for child in list(cell.childNodes):
                        cell.removeChild(child)
                    # Write new value
                    p = P(text=str(value))
                    cell.addElement(p)
                    return
    raise ValueError(f"Cell ({target_row}, {target_col}) not found")

# --- Test read ---
sn = get_cell_value(get_cell(sheet, 54, 2))
print(f"TC SN at row 54 col 2: '{sn}'")

# --- Test write ---
set_cell_value(sheet, 54, 3, "TEST_VALUE")
written = get_cell_value(get_cell(sheet, 54, 3))
print(f"Written to row 54 col 3: '{written}'")

# --- Save to new file ---
doc.save(OUT_PATH)
print(f"Saved to {OUT_PATH}")
print("Open ITP_TEST_OUTPUT.ods and check row 54 col 3 has TEST_VALUE")
