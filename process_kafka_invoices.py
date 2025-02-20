from kafka import KafkaConsumer
import pandas as pd
import json
import os

# ✅ Initialize Kafka Consumer
consumer = KafkaConsumer(
    "invoices",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x and x.strip() else None  # ✅ Handle empty messages
)

print("🚀 Kafka Consumer Started! Waiting for messages...")

# ✅ Collect messages into a DataFrame
invoices = []
for message in consumer:
    try:
        if message.value:  # ✅ Ensure the message is not empty
            invoices.append(message.value)
            print(f"✅ Received: {message.value}")
        else:
            print("⚠️ Skipping empty message")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON: {message.value}")

    if len(invoices) >= 3:  # Process only 3 messages
     break


# ✅ Convert to Pandas DataFrame
if invoices:
    print(f"📊 Total invoices collected: {len(invoices)}")
    df = pd.DataFrame(invoices)
    print("📊 DataFrame Created:")
    print(df.head())

    # ✅ Save to CSV
    df.to_csv("invoices.csv", index=False)
    print(f"📂 CSV File Created: invoices.csv Exists? {os.path.exists('invoices.csv')}")

    # ✅ Save to Parquet
    df.to_parquet("invoices.parquet", index=False)
    print(f"📂 Parquet File Created: invoices.parquet Exists? {os.path.exists('invoices.parquet')}")

    print("✅ Invoices saved successfully!")
else:
    print("⚠️ No valid invoices found.")
