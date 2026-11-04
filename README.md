# DecodeLabs-Internship
Data Analytics internship projects
## Project 1: Data Cleaning & Preparation
Turned a raw e-commerce orders dataset into a verified, analysis-ready dataset, with every change documented.
### Dataset
- 1,200 orders, 14 columns (OrderID, Date, CustomerID, Product, Quantity, UnitPrice, ShippingAddress, PaymentMethod, OrderStatus, TrackingNumber, ItemsInCart, CouponCode, ReferralSource, TotalPrice)
- Only CouponCode had missing values (309 blanks)

### Method (Python, pandas)
| ID | Change | Impact |
|---|---|---|
| CR001 | Imputed missing `CouponCode` using the **mode** (categorical column) | 309 blanks filled, 1,200 records preserved |
| CR002 | Audited and removed duplicate `OrderID`s (keep first) | 0 duplicates found, 0 rows removed |
| CR003 | Standardized `Date` to ISO 8601 (`YYYY-MM-DD`) | 100% of dates compliant |
| CR004 | Trimmed whitespace and applied Title Case to text columns | Text normalized |
| CR005 | Rounded `UnitPrice` and `TotalPrice` to 2 decimals | Floating-point artifacts removed |

### Verification gate
| Check | Result |
|---|---|
| Duplicate OrderIDs | **0** |
| Incorrectly formatted dates | **0** |
| Nulls in critical fields | **0** |
| Max decimals in UnitPrice / TotalPrice | 2 |
| Rows before / after | 1,200 / 1,200 |

### Files
- `ecommerce-orders-raw dataset.xlsx`: original raw data
- `ecommerce-orders-clean dataset.xlsx`: cleaned dataset
- `clean_orders.py`: reproducible cleaning script (also generates the report PDF)
- `Change_log.pdf`: change log and verification report

### How to run
```bash
pip install pandas numpy openpyxl reportlab
python clean_orders.py
```
Keep the raw Excel file in the same folder and make sure its name matches the one in the script.

### Note
Blank `CouponCode` values were imputed with the mode, following the course guidance for categorical columns. This assumes a blank is a missing value. If blanks mean "no coupon used", a `"No Coupon"` label would be the more accurate choice.
