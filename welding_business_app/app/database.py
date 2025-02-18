import sqlite3

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            brand TEXT,
            quantity INTEGER,
            price REAL
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items TEXT,
            total_bill REAL
        )
        """)
        self.conn.commit()

    def add_item(self, item, brand, quantity, price):
        self.cursor.execute("INSERT INTO inventory (item, brand, quantity, price) VALUES (?, ?, ?, ?)", (item, brand, quantity, price))
        self.conn.commit()

    def get_inventory(self):
        return self.cursor.execute("SELECT * FROM inventory").fetchall()

    def update_item(self, item_id, quantity, price):
        self.cursor.execute("UPDATE inventory SET quantity = ?, price = ? WHERE id = ?", (quantity, price, item_id))
        self.conn.commit()

    def delete_item(self, item_id):
        self.cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        self.conn.commit()

    def add_invoice(self, customer_name, items, total_bill):
        self.cursor.execute("INSERT INTO invoices (customer_name, items, total_bill) VALUES (?, ?, ?)", (customer_name, items, total_bill))
        self.conn.commit()

    def get_invoices(self):
        return self.cursor.execute("SELECT * FROM invoices").fetchall()