import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import json
import datetime
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Ensure the app module is found
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the database module
try:
    from app.database import Database
except ModuleNotFoundError:
    st.error("⚠️ Module 'app.database' not found! Ensure the project structure is correct.")

# Initialize database connection
try:
    db = Database("data/welding_business.db")
except Exception as e:
    st.error(f"❌ Database Connection Error: {e}")

# Set Streamlit page configuration
st.set_page_config(page_title="Wel-Wishers Business App", page_icon="🌟", layout="wide")

# Inject Custom CSS
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Custom CSS file 'style.css' not found. Skipping styles.")

# ✅ Inventory Management
def manage_inventory():
    st.header("📦 Manage Inventory")

    # Add New Item
    with st.form("add_item_form"):
        st.subheader("➕ Add New Item")
        item = st.text_input("Item Name")
        brand = st.text_input("Brand")
        quantity = st.number_input("Quantity", min_value=1)
        price = st.number_input("Price (₹)", min_value=0.0)

        if st.form_submit_button("Add Item"):
            if item and brand and quantity and price:
                db.add_item(item, brand, quantity, price)
                st.success(f"✅ '{item}' added successfully!")
            else:
                st.error("⚠️ Please fill in all fields.")

    # Display Inventory
    try:
        inventory = db.get_inventory()
        if inventory:
            df = pd.DataFrame(inventory, columns=["ID", "Item", "Brand", "Quantity", "Price"])
            st.dataframe(df)
        else:
            st.info("ℹ️ No items found in inventory.")
    except Exception as e:
        st.error(f"❌ Error loading inventory: {e}")

# ✅ Invoice Generator
def generate_invoice():
    st.header("🧾 Generate Invoice")

    customer_name = st.text_input("Customer Name")
    customer_contact = st.text_input("Customer Contact Number")

    if st.button("📄 Generate Invoice"):
        if customer_name and customer_contact:
            st.success(f"✅ Invoice for {customer_name} generated successfully!")
        else:
            st.error("⚠️ Please enter valid customer details.")

# ✅ Function to Capture Streamlit Output as Static HTML
def save_as_static_html():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)

    app_url = "http://localhost:8501"
    driver.get(app_url)
    time.sleep(5)  # Allow some time for rendering

    # Save HTML output
    os.makedirs("static", exist_ok=True)
    with open("static/index.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    driver.quit()
    st.success("✅ Static HTML generated! Check 'static/index.html'.")

# ✅ Main Function
def main():
    st.title("🌟 Welding Business Management App")
    
    menu = st.sidebar.radio("Navigation", ["Inventory", "Generate Invoice"])

    if menu == "Inventory":
        manage_inventory()
    elif menu == "Generate Invoice":
        generate_invoice()

    # Button to Generate Static HTML
    if st.button("Generate Static HTML"):
        save_as_static_html()

if __name__ == "__main__":
    main()
