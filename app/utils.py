def calculate_total_bill(items):
    return sum(item["quantity"] * item["price"] for item in items)