
from pathlib import Path
from datetime import date, timedelta
import random

import pandas as pd
from faker import Faker

fake = Faker("en_GB")
Faker.seed(42)
random.seed(42)

OUTPUT = Path("data/raw")
OUTPUT.mkdir(parents=True, exist_ok=True)

medicine_names = [
    "Paracetamol 500mg",
    "Ibuprofen 200mg",
    "Cetirizine 10mg",
    "Vitamin C 1000mg",
    "Aspirin 75mg",
    "Omeprazole 20mg",
    "Loratadine 10mg",
    "Amoxicillin 250mg",
    "Metformin 500mg",
    "Salbutamol Inhaler",
]

categories = [
    "Pain Relief",
    "Allergy",
    "Vitamins",
    "Digestive Health",
    "Prescription",
]

medicines = []

for i in range(1, 31):
    base_name = medicine_names[(i - 1) % len(medicine_names)]

    medicines.append({
        "medicine_id": f"MED{i:03d}",
        "medicine_name": f"{base_name} - Pack {i}",
        "category": random.choice(categories),
        "unit_price": round(random.uniform(1.50, 35.00), 2),
    })

suppliers = []

for i in range(1, 13):
    suppliers.append({
        "supplier_id": f"SUP{i:03d}",
        "supplier_name": f"{fake.company()} Pharma",
        "city": fake.city(),
    })

branches = []

for i in range(1, 9):
    branches.append({
        "branch_id": f"BR{i:03d}",
        "branch_name": f"PharmaFlow Branch {i}",
        "city": fake.city(),
    })

start_date = date(2026, 1, 1)

retail_sales = []

for i in range(1, 10001):
    medicine = random.choice(medicines)
    branch = random.choice(branches)
    quantity = random.randint(1, 15)

    retail_sales.append({
        "sale_id": f"SALE{i:06d}",
        "sale_date": (
            start_date + timedelta(days=random.randint(0, 270))
        ).isoformat(),
        "branch_id": branch["branch_id"],
        "medicine_id": medicine["medicine_id"],
        "quantity": quantity,
        "unit_price": medicine["unit_price"],
        "total_amount": round(
            quantity * medicine["unit_price"], 2
        ),
    })

wholesale_orders = []

for i in range(1, 3001):
    medicine = random.choice(medicines)
    supplier = random.choice(suppliers)
    quantity = random.randint(20, 500)
    unit_cost = round(medicine["unit_price"] * 0.65, 2)

    wholesale_orders.append({
        "order_id": f"ORD{i:06d}",
        "order_date": (
            start_date + timedelta(days=random.randint(0, 270))
        ).isoformat(),
        "supplier_id": supplier["supplier_id"],
        "medicine_id": medicine["medicine_id"],
        "quantity": quantity,
        "unit_cost": unit_cost,
        "total_cost": round(quantity * unit_cost, 2),
    })

datasets = {
    "medicines.csv": medicines,
    "suppliers.csv": suppliers,
    "branches.csv": branches,
    "retail_sales.csv": retail_sales,
    "wholesale_orders.csv": wholesale_orders,
}

for filename, records in datasets.items():
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT / filename, index=False)
    print(f"Created {filename}: {len(df):,} rows")

print("All synthetic pharmacy datasets generated.")
