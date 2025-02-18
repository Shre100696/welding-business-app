from dataclasses import dataclass

@dataclass
class InventoryItem:
    item: str
    brand: str
    quantity: int
    price: float

@dataclass
class Invoice:
    customer_name: str
    items: str
    total_bill: float