import streamlit as st
from app.database import Database
import pandas as pd

# Initialize database
db = Database("data/welding_business.db")

# Custom CSS for UI improvements
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
    </style>
    """, unsafe_allow_html=True)

def manage_inventory():
    st.header("Manage Inventory")

    # Add new item
    with st.form("add_item_form"):
        st.write("Add New Item")
        item = st.text_input("Item Name", help="Enter the name of the item")
        brand = st.text_input("Brand", help="Enter the brand of the item")
        quantity = st.number_input("Quantity", min_value=1, help="Enter the quantity of the item")
        price = st.number_input("Price", min_value=0.0, help="Enter the price of the item")
        if st.form_submit_button("Add Item"):
            if item and brand and quantity and price:
                db.add_item(item, brand, quantity, price)
                st.success("Item added successfully!")
            else:
                st.error("Please fill in all fields.")

    # Display inventory
    st.write("Current Inventory")
    inventory = db.get_inventory()
    if inventory:
        st.table(pd.DataFrame(inventory, columns=["ID", "Item", "Brand", "Quantity", "Price"]))
    else:
        st.info("No items in inventory.")

    # Update item
    with st.form("update_item_form"):
        st.write("Update Item")
        item_id = st.number_input("Item ID to Update", min_value=1, help="Enter the ID of the item to update")
        new_quantity = st.number_input("New Quantity", min_value=0, help="Enter the new quantity")
        new_price = st.number_input("New Price", min_value=0.0, help="Enter the new price")
        if st.form_submit_button("Update Item"):
            if item_id and (new_quantity or new_price):
                db.update_item(item_id, new_quantity, new_price)
                st.success("Item updated successfully!")
            else:
                st.error("Please provide valid inputs.")

    # Delete item
    with st.form("delete_item_form"):
        st.write("Delete Item")
        item_id = st.number_input("Item ID to Delete", min_value=1, help="Enter the ID of the item to delete")
        if st.form_submit_button("Delete Item"):
            if item_id:
                db.delete_item(item_id)
                st.success("Item deleted successfully!")
            else:
                st.error("Please provide a valid item ID.")

def generate_invoice():
    st.header("Generate Invoice")

    # Select customer name
    customer_name = st.text_input("Customer Name", help="Enter the customer's name")

    # Select items
    inventory = db.get_inventory()
    if not inventory:
        st.warning("No items in inventory. Please add items first.")
        return

    selected_items = []
    total_bill = 0.0
    for item in inventory:
        item_id, item_name, brand, quantity, price = item
        item_key = f"{item_id}_{item_name}"
        item_quantity = st.number_input(
            f"Quantity for {item_name} ({brand})",
            min_value=0,
            max_value=quantity,
            key=item_key,
            help=f"Available: {quantity}"
        )
        if item_quantity > 0:
            selected_items.append({
                "item_id": item_id,
                "item_name": item_name,
                "brand": brand,
                "quantity": item_quantity,
                "price": price,
                "total": item_quantity * price
            })
            total_bill += item_quantity * price

    # Display selected items and total bill
    if selected_items:
        st.write("Selected Items")
        st.table(pd.DataFrame(selected_items))
        st.write(f"**Total Bill: ₹{total_bill:.2f}**")

        # Generate invoice
        if st.button("Generate Invoice"):
            if customer_name:
                items_str = ", ".join([f"{item['item_name']} ({item['brand']}) - {item['quantity']} pcs" for item in selected_items])
                db.add_invoice(customer_name, items_str, total_bill)
                st.success("Invoice generated successfully!")
            else:
                st.error("Please enter the customer name.")
    else:
        st.info("No items selected.")

def view_invoices():
    st.header("View Invoices")

    invoices = db.get_invoices()
    if invoices:
        st.table(pd.DataFrame(invoices, columns=["ID", "Customer Name", "Items", "Total Bill"]))
    else:
        st.info("No invoices found.")

def main():
    st.title("Welding Business Management App")
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Choose an option", ["Inventory", "Generate Invoice", "View Invoices"])

    if menu == "Inventory":
        manage_inventory()
    elif menu == "Generate Invoice":
        generate_invoice()
    elif menu == "View Invoices":
        view_invoices()

if __name__ == "__main__":
    main()