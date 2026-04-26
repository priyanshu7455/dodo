import sqlite3
import pandas as pd
import streamlit as st
from datetime import date


# ---------------- INIT DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect("expenses.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

# Call it once
init_db()

# ---------------- DATABASE FUNCTIONS ---------------- #

def connect_db():
    return sqlite3.connect("expenses.db", check_same_thread=False)

def add_expense(amount, category, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
        (amount, category, date)
    )
    conn.commit()
    conn.close()

def get_expenses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    data = cursor.fetchall()
    conn.close()
    return data

def get_total():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def category_summary():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses GROUP BY category"
    )
    data = cursor.fetchall()
    conn.close()
    return data

def delete_expense(expense_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

def update_expense(expense_id, amount, category, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET amount=?, category=?, date=? WHERE id=?",
        (amount, category, date, expense_id)
    )
    conn.commit()
    conn.close()


# ---------------- UI SECTION ---------------- #

st.title("💰 Smart Expense Tracker")
st.write("Track your daily expenses easily 🚀")

# -------- ADD EXPENSE -------- #

st.subheader("➕ Add New Expense")

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Amount", min_value=0.0)

with col2:
    category = st.text_input("Category")

date_input = st.date_input("Date", date.today())

if st.button("Add Expense"):
    if amount and category:
        add_expense(amount, category, str(date_input))
        st.success("Expense Added Successfully ✅")
    else:
        st.warning("Please fill all fields")

st.write("---")

# -------- METRICS -------- #

col1, col2 = st.columns(2)

with col1:
    st.metric("💰 Total Expense", get_total() or 0)

with col2:
    st.metric("📊 Total Entries", len(get_expenses()))

st.write("---")

# -------- TABLE -------- #

st.subheader("📋 All Expenses")

data = get_expenses()

if data:
    df = pd.DataFrame(data, columns=["ID", "Amount", "Category", "Date"])
    st.dataframe(df)
else:
    st.info("No expenses added yet")

st.write("---")

# -------- DELETE FEATURE -------- #

st.subheader("🗑️ Delete Expense")

delete_id = st.number_input("Enter ID to delete", min_value=1, step=1)

if st.button("Delete Expense"):
    delete_expense(delete_id)
    st.warning(f"Expense with ID {delete_id} deleted")

st.write("---")

# -------- UPDATE FEATURE -------- #

st.subheader("✏️ Update Expense")

update_id = st.number_input("Enter ID to update", min_value=1, step=1)

col1, col2 = st.columns(2)

with col1:
    new_amount = st.number_input("New Amount", min_value=0.0, key="upd_amt")

with col2:
    new_category = st.text_input("New Category", key="upd_cat")

new_date = st.date_input("New Date", date.today(), key="upd_date")

if st.button("Update Expense"):
    if new_amount and new_category:
        update_expense(update_id, new_amount, new_category, str(new_date))
        st.success("Expense Updated Successfully ✨")
    else:
        st.warning("Fill all update fields")

st.write("---")

# -------- CHART -------- #

st.subheader("📊 Expense Distribution")

summary = category_summary()

if summary:
    df_summary = pd.DataFrame(summary, columns=["Category", "Total"])
    st.bar_chart(df_summary.set_index("Category"))
else:
    st.info("No data for chart")