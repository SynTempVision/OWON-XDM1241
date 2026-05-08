from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P

def get_cell_value(cell):
    ps = cell.getElementsByType(P)
    parts = []
    for p in ps:
        text = "".join(str(n) for n in p.childNodes if hasattr(n, 'data'))
        parts.append(text)
    return " ".join(parts).strip()

doc = load(r"C:\Users\synte\Downloads\ITP.0002_1ElementStandard_Rev0.ods")

for sheet in doc.spreadsheet.getElementsByType(Table):
    print(f"\n=== Sheet: {sheet.getAttribute('name')} ===")
    for row_idx, row in enumerate(sheet.getElementsByType(TableRow), start=1):
        for col_idx, cell in enumerate(row.getElementsByType(TableCell), start=1):
            val = get_cell_value(cell)
            if val:
                print(f"  Row {row_idx:3d}  Col {col_idx:3d}  |  {val}")
