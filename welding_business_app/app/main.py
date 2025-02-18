import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from app.database import Database
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import datetime

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Initialize database connection
db = Database("data/welding_business.db")

# Set Streamlit page configuration
st.set_page_config(page_title="Wel-Wishers Business App", page_icon="🌟", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
    }
    .stTextInput input, .stNumberInput input {
        border-radius: 5px;
    }
    .stHeader {
        color: #4CAF50;
    }
    .block-container {
        padding: 1rem 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("assets/logo.png", width=150)  # Add company logo
st.sidebar.title("🌟 Wel-Wishers Business App")
menu = st.sidebar.radio("Navigation", ["Inventory", "Generate Invoice", "View Invoices"])

# Function to Generate Invoice PDF
def generate_invoice_pdf(customer_name, customer_contact, selected_items, total_bill):
    """Generate a PDF invoice and return the file path"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_filename = f"Invoice_{customer_name.replace(' ', '_')}_{timestamp}.pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf_path = tmpfile.name
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(220, 750, "Wel-Wishers Invoice")
        c.setFont("Helvetica", 12)

        # Customer details
        c.drawString(50, 720, f"Customer Name: {customer_name}")
        c.drawString(50, 700, f"Contact: {customer_contact}")
        c.drawString(50, 680, f"Date: {timestamp}")

        # Table Header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 650, "Item")
        c.drawString(250, 650, "Brand")
        c.drawString(350, 650, "Quantity")
        c.drawString(450, 650, "Price (₹)")
        c.drawString(500, 650, "Total (₹)")
        c.line(50, 645, 550, 645)

        # Items in invoice
        y_position = 625
        for item in selected_items:
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position, item['item_name'])
            c.drawString(250, y_position, item['brand'])
            c.drawString(350, y_position, str(item['quantity']))
            c.drawString(450, y_position, f"₹{item['price']:.2f}")
            c.drawString(500, y_position, f"₹{item['total']:.2f}")
            y_position -= 20

        # Total Bill
        c.line(50, y_position - 10, 550, y_position - 10)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y_position - 30, "Total Bill:")
        c.drawString(500, y_position - 30, f"₹{total_bill:.2f}")

        c.save()

    return pdf_path

# Generate Invoice
def generate_invoice():
    st.header("🧾 Generate Invoice")

    # Enter Customer Details
    customer_name = st.text_input("Customer Name", help="Enter the customer's name")
    customer_contact = st.text_input("Customer Contact Number", help="Enter contact number")

    # Fetch Inventory Data
    inventory = db.get_inventory()
    if not inventory:
        st.warning("⚠️ No items available. Please add items first.")
        return

    # Select Items and Quantities
    selected_items = []
    total_bill = 0.0
    for item in inventory:
        item_id, item_name, brand, quantity, price = item
        col1, col2, col3 = st.columns([2, 1, 1])
        item_selected_quantity = col2.number_input(
            f"{item_name} ({brand})", 
            min_value=0, 
            max_value=quantity, 
            key=f"{item_id}_{item_name}",
            help=f"Available: {quantity}"
        )
        if item_selected_quantity > 0:
            selected_items.append({
                "item_id": item_id,
                "item_name": item_name,
                "brand": brand,
                "quantity": item_selected_quantity,
                "price": price,
                "total": item_selected_quantity * price
            })
            total_bill += item_selected_quantity * price

    # Display Selected Items
    if selected_items:
        st.subheader("🛒 Selected Items")
        st.table(pd.DataFrame(selected_items))
        st.write(f"**💰 Total Bill: ₹{total_bill:.2f}**")

        # Generate Invoice Button
        if st.button("📄 Generate Invoice"):
            if customer_name and customer_contact:
                items_str = ", ".join([f"{item['item_name']} ({item['brand']}) - {item['quantity']} pcs" for item in selected_items])
                db.add_invoice(customer_name, items_str, total_bill)
                st.success(f"✅ Invoice for {customer_name} generated successfully!")

                # Generate PDF
                pdf_path = generate_invoice_pdf(customer_name, customer_contact, selected_items, total_bill)

                # Provide download link for PDF
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Invoice PDF",
                        data=file,
                        file_name=f"Invoice_{customer_name}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("⚠️ Please enter the customer name and contact number.")
    else:
        st.info("ℹ️ No items selected.")

# --- Main App ---
def main():
    st.title("🌟 Welding Business Management App")
    
    if menu == "Inventory":
        manage_inventory()
    elif menu == "Generate Invoice":
        generate_invoice()
    elif menu == "View Invoices":
        view_invoices()

if __name__ == "__main__":
    main()
