import pandas as pd
from datetime import datetime

# Load cleaned CSV
df = pd.read_csv("clean_transactions.csv")

# Ensure proper types
df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# -----------------------------
# Salary (MPOWER)
# -----------------------------
salary_df = df[df["Remarks"].str.upper().str.contains("MPOWER", na=False)].copy()
salary_total = salary_df["Credit"].sum()

# -----------------------------
# Dividends (NACH)
# -----------------------------
dividend_df = df[
    df["Remarks"].str.upper().str.contains("NACH", na=False)
    | df["Remarks"].str.upper().str.contains("INT.PD", na=False)
].copy()
dividend_total = dividend_df["Credit"].sum()

# -----------------------------
# Other Credits > 5000
# -----------------------------
# get all other credits ignoring the salary and dividents above 5000
other_df = df[
    (df["Credit"] > 5000)
    & (~df["Remarks"].str.upper().str.contains("MPOWER", na=False))
    & (~df["Remarks"].str.upper().str.contains("NACH", na=False))  # stocks dividents
    & (~df["Remarks"].str.upper().str.contains("INT.PD", na=False))  # bank dividents
    # & (~df["Remarks"].str.upper().str.contains("INTEREST", na=False))
].copy()
other_total = other_df["Credit"].sum()

# -----------------------------
# Generate Markdown
# -----------------------------
md_report = []

# Salary Section
md_report.append("## 💼 Salary Transactions (MPOWER)\n")
md_report.append(salary_df[["Date", "Remarks", "Credit"]].to_markdown(index=False))
md_report.append(f"\n**Total Salary Credited: ₹{salary_total:,.2f}**\n")

# Dividend Section
md_report.append(
    "## 💰 Dividend Transactions (NACH) [from stocks] + INT.pd [from bank] \n"
)
md_report.append(dividend_df[["Date", "Remarks", "Credit"]].to_markdown(index=False))
md_report.append(f"\n**Total Dividends Credited: ₹{dividend_total:,.2f}**\n")

# Other Credits Section
md_report.append("## 📥 Other Credit Transactions (> ₹5000)\n")
md_report.append(other_df[["Date", "Remarks", "Credit"]].to_markdown(index=False))
md_report.append(f"\n**Total Other Credits (>5000): ₹{other_total:,.2f}**\n")

md_report.append(
    f"TOTAL CREDITED FOR INCOME TAX CALC : {salary_total + dividend_total + other_total}"
)

df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")

# Find the largest debit transaction
biggest_exp = df.loc[df["Debit"].idxmax()].copy()

# Extract details
biggest_exp_date = biggest_exp["Date"]
biggest_exp_remarks = biggest_exp["Remarks"]
biggest_exp_amount = biggest_exp["Debit"]

# Add to Markdown report
md_report.append("## 💸 Biggest Expenditure\n")
md_report.append(
    f"- **Date:** {biggest_exp_date.strftime('%Y-%m-%d')}\n"
    f"- **Remarks:** {biggest_exp_remarks}\n"
    f"- **Amount:** ₹{biggest_exp_amount:,.2f}\n"
)

# Save to file
with open("bank_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_report))

print("✅ Markdown report generated: bank_report.md")

    
