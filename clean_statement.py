import re

import pandas as pd
import pdfplumber

# -----------------------------
# Step 1: Extract text from PDF
# -----------------------------
pdf_file = "statements/statement_unlocked.pdf"
all_text = ""

with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        all_text += page.extract_text() + "\n"

# -----------------------------
# Step 2: Regex to capture transactions
# -----------------------------
pattern = re.compile(
    r"(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\S+)\s+(.+?)\s+([\d,]+\.\d{2})\s+\((Dr|Cr)\)\s+([\d,]+\.\d{2})\s+\(Cr\)",
    re.MULTILINE,
)

transactions = []
for match in pattern.finditer(all_text):
    sno, date, txn_id, remarks, amount, drcr, balance = match.groups()
    transactions.append(
        {
            "S.No": int(sno),
            "Date": pd.to_datetime(date, format="%d/%m/%Y"),
            "Transaction Id": txn_id,
            "Remarks": remarks.strip(),
            "Amount": float(amount.replace(",", "")),
            "Type": drcr,  # Dr or Cr
            "Balance": float(balance.replace(",", "")),
        }
    )

# -----------------------------
# Step 3: Convert to DataFrame
# -----------------------------
df = pd.DataFrame(transactions)

# Split Debit and Credit
df["Debit"] = df.apply(lambda x: x["Amount"] if x["Type"] == "Dr" else 0, axis=1)
df["Credit"] = df.apply(lambda x: x["Amount"] if x["Type"] == "Cr" else 0, axis=1)

# Drop helper columns
df = df.drop(columns=["Amount", "Type"])

# Sort by Date
df = df.sort_values("Date").reset_index(drop=True)

# -----------------------------
# Step 4: Save & Analyze
# -----------------------------
df.to_csv("reports/clean_transactions.csv", index=False)

print(df.head(10))
print("\nTotal Debits:", df["Debit"].sum())
print("Total Credits:", df["Credit"].sum())

monthly = df.groupby(df["Date"].dt.to_period("M"))[["Debit", "Credit"]].sum()
print("\nMonthly Summary:")
print(monthly)
