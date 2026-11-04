import pandas as pd
import numpy as np

# Load the raw data
df = pd.read_excel("Dataset for Data Analytics.xlsx", sheet_name="Sheet1")

print("Shape:", df.shape)
print(df.dtypes)
print(df.isnull().sum())

# --- Missing values audit ---
missing = df.isnull().sum()
print("Missing values per column:\n", missing[missing > 0])

# --- Duplicate audit (Phase 2: Integrity Audit) ---
dup_orders = df[df.duplicated(subset=["OrderID"], keep=False)]
print(f"Duplicate OrderIDs: {len(dup_orders)}")
print(f"Fully duplicated rows: {df.duplicated().sum()}")

# --- Format audit ---
print("\nCouponCode unique values:", df["CouponCode"].unique())  # NaN + strings
print("Date dtype:", df["Date"].dtype)
print("ShippingAddress sample:", df["ShippingAddress"].head().tolist())
print("TotalPrice sample:", df["TotalPrice"].head().tolist())  # floats w/ precision issues

# --- CouponCode: categorical → impute with MODE, or a placeholder ---
# Option A (PDF-aligned: use MODE)
mode_coupon = df["CouponCode"].mode()[0]
df["CouponCode"] = df["CouponCode"].fillna(mode_coupon)

# --- Identify duplicate OrderIDs ---
dupes = df[df.duplicated(subset=["OrderID"], keep=False)]
print(f"Rows with duplicated OrderID: {len(dupes)}")

# --- Remove duplicates (keep first occurrence) ---
df = df.drop_duplicates(subset=["OrderID"], keep="first").reset_index(drop=True)

# --- Verify: zero duplicate OrderIDs ---
assert df["OrderID"].duplicated().sum() == 0, "Duplicate OrderIDs remain!"
print("✅ Zero duplicate OrderIDs")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Verify no failed parses
assert df["Date"].isnull().sum() == 0, "Some dates failed parsing"

# Store as ISO 8601 date string (YYYY-MM-DD)
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

print(df["Date"].head())

text_cols = ["Product", "ShippingAddress", "PaymentMethod", "OrderStatus", "ReferralSource"]

for col in text_cols:
    df[col] = df[col].astype(str).str.strip().str.title()

print(df["Product"].unique())
print(df["PaymentMethod"].unique())

df["UnitPrice"] = df["UnitPrice"].round(2)
df["TotalPrice"] = df["TotalPrice"].round(2)

# Optional: verify TotalPrice ≈ Quantity * UnitPrice
mismatch = df[~np.isclose(df["TotalPrice"], df["Quantity"] * df["UnitPrice"], atol=0.02)]
print(f"Rows where TotalPrice ≠ Qty × UnitPrice (within 0.02): {len(mismatch)}")

# --- Criterion 1: Zero duplicate IDs ---
assert df["OrderID"].duplicated().sum() == 0
print("✅ 0 duplicate OrderIDs")

# --- Criterion 2: Zero incorrectly formatted dates ---
iso_pattern = r"^\d{4}-\d{2}-\d{2}$"
bad_dates = df[~df["Date"].str.match(iso_pattern)]
assert len(bad_dates) == 0
print("✅ 0 incorrectly formatted dates (all ISO 8601)")

# --- Bonus: no missing values in critical fields ---
critical = ["OrderID", "Date", "CustomerID", "Product", "Quantity",
            "UnitPrice", "PaymentMethod", "OrderStatus", "TotalPrice"]
assert df[critical].isnull().sum().sum() == 0
print("✅ No nulls in critical fields")

# --- Bonus: numeric precision ---
assert (df["UnitPrice"].apply(lambda x: len(str(x).split(".")[-1]) <= 2)).all()
assert (df["TotalPrice"].apply(lambda x: len(str(x).split(".")[-1]) <= 2)).all()
print("✅ Numeric precision = 2 decimals")

print("\nFinal shape:", df.shape)

change_log = pd.DataFrame([
    {"Change ID": "CR001",
     "Description": "Imputed missing 'CouponCode' using MODE",
     "Impact": f"Preserved {df.shape[0]} records",
     "Status": "Resolved"},
    {"Change ID": "CR002",
     "Description": "Removed duplicate OrderIDs (keep first)",
     "Impact": "Zero duplicate IDs achieved",
     "Status": "Resolved"},
    {"Change ID": "CR003",
     "Description": "Standardized 'Date' to ISO 8601 (YYYY-MM-DD)",
     "Impact": "100% dates conform to ISO 8601",
     "Status": "Resolved"},
    {"Change ID": "CR004",
     "Description": "Applied Title Case + Trim to text columns",
     "Impact": "Product/PaymentMethod/OrderStatus/ReferralSource normalized",
     "Status": "Resolved"},
    {"Change ID": "CR005",
     "Description": "Rounded UnitPrice & TotalPrice to 2 decimals",
     "Impact": "Eliminated floating-point artifacts (e.g., 769.3799999999999 → 769.38)",
     "Status": "Resolved"},
])

print(change_log.to_string(index=False))

# Export the change log
change_log.to_csv("change_log.csv", index=False)
# Or, to produce a PDF (as the PDF asks), uncomment:
# change_log.to_latex("change_log.tex")   # then compile, or use reportlab/fpdf

output_path = "Dataset_Cleaned_Project1.xlsx"
df.to_excel(output_path, index=False)
print(f"✅ Clean file saved to: {output_path}")

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
import pandas as pd
import numpy as np

# ---------- Assume df is already cleaned (end of previous script) ----------
# df = pd.read_excel("Dataset_Cleaned_Project1.xlsx")
# ---------------------------------------------------------------------------

PDF_PATH = "Project1_Cleaning_Report.pdf"

doc = SimpleDocTemplate(
    PDF_PATH,
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="DecodeLabs Project 1 – Data Cleaning Report",
    author="Your Name",
)

styles = getSampleStyleSheet()
title_style    = styles["Title"]
heading_style  = styles["Heading2"]
body_style     = styles["BodyText"]

# Custom style for the big shape line
shape_style = ParagraphStyle(
    "ShapeStyle", parent=body_style,
    fontSize=14, leading=18, textColor=colors.HexColor("#1f4e79"),
)

# Custom style for table cells to handle wrapping
cell_style = ParagraphStyle(
    name="TableCell",
    fontName="Helvetica",
    fontSize=9,
    leading=11,
)

story = []

# ---------- Title ----------
story.append(Paragraph("DecodeLabs – Project 1", title_style))
story.append(Paragraph("Data Cleaning &amp; Preparation Report", heading_style))
story.append(Spacer(1, 0.4*cm))

# ---------- Final Shape ----------
story.append(Paragraph("<b>Final Dataset Shape</b>", heading_style))

rows = df.shape[0]
cols = df.shape[1]

story.append(Paragraph(
    f"Final shape: <b>{rows:,} rows × {cols} columns</b>", shape_style
))
story.append(Spacer(1, 0.3*cm))

# ---------- Quick integrity metrics table ----------
story.append(Paragraph("<b>Verification Checklist</b>", heading_style))

checks = [
    ["Check", "Result"],
    ["Duplicate OrderIDs",          f"{df['OrderID'].duplicated().sum()}"],
    ["Rows failing ISO-8601 dates", f"{(~df['Date'].astype(str).str.match(r'^\\d{{4}}-\\d{{2}}-\\d{{2}}$')).sum()}"],
    ["Nulls in critical fields",
     f"{df[['OrderID','Date','CustomerID','Product','Quantity','UnitPrice','PaymentMethod','OrderStatus','TotalPrice']].isnull().sum().sum()}"],
    ["Max decimals in UnitPrice",
     f"{df['UnitPrice'].astype(str).str.split('.').str[-1].str.len().max()}"],
    ["Max decimals in TotalPrice",
     f"{df['TotalPrice'].astype(str).str.split('.').str[-1].str.len().max()}"],
]

tbl = Table(checks, colWidths=[9*cm, 4*cm])
tbl.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#1f4e79")),
    ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE",     (0,0), (-1,-1), 10),
    ("ALIGN",        (1,0), (1,-1), "CENTER"),
    ("GRID",         (0,0), (-1,-1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",   (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
]))
story.append(tbl)
story.append(Spacer(1, 0.6*cm))

# ---------- Optional: Change Log table ----------
story.append(Paragraph("<b>Change Log</b>", heading_style))

# Wrap text in Paragraphs for the Description and Impact columns
change_log = [
    ["Change ID", "Description", "Impact", "Status"],
    ["CR001", Paragraph("Imputed missing 'CouponCode' using mode", cell_style),
     Paragraph(f"Preserved {rows:,} records", cell_style), "Resolved"],
    ["CR002", Paragraph("Removed duplicate OrderIDs", cell_style),
     Paragraph("0 duplicate IDs", cell_style), "Resolved"],
    ["CR003", Paragraph("Standardized 'Date' to ISO-8601 (YYYY-MM-DD)", cell_style),
     Paragraph("100% compliant", cell_style), "Resolved"],
    ["CR004", Paragraph("Title-cased + trimmed text columns", cell_style),
     Paragraph("Normalized text", cell_style), "Resolved"],
    ["CR005", Paragraph("Rounded UnitPrice & TotalPrice to 2 decimals", cell_style),
     Paragraph("Fixed float artifacts", cell_style), "Resolved"],
]

# Adjusted column widths to fill the 17cm usable page width perfectly
cl_tbl = Table(change_log, colWidths=[2.2*cm, 6.5*cm, 5.5*cm, 2.8*cm])
cl_tbl.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#1f4e79")),
    ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",     (0,1), (0,-1), "Helvetica"), # Only apply font to ID/Status strings
    ("FONTNAME",     (3,1), (3,-1), "Helvetica"),
    ("FONTSIZE",     (0,0), (-1,-1), 9),
    ("ALIGN",        (0,0), (0,-1), "CENTER"),
    ("ALIGN",        (3,0), (3,-1), "CENTER"),
    ("GRID",         (0,0), (-1,-1), 0.4, colors.grey),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"), # Center vertically
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
    ("TOPPADDING",   (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
]))
story.append(cl_tbl)

# ---------- Build ----------
doc.build(story)
print(f"✅ PDF report saved to: {PDF_PATH}")
