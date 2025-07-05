import sqlite3
import time

# Constants
FIVE_YEARS_IN_SECONDS = 5 * 365 * 24 * 60 * 60  # 5 years in seconds
current_time = int(time.time())
max_next_rep = current_time + FIVE_YEARS_IN_SECONDS

# Connect to the database
db_path = "path/to/your/database.db"  # Replace with the actual path to your database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all cards with their next_rep values
query = "SELECT id, next_rep FROM cards"
cursor.execute(query)
cards = cursor.fetchall()

# Update next_rep values proportionally
for card_id, next_rep in cards:
    if next_rep > max_next_rep:
        # Proportionally compress next_rep to within 5 years
        compressed_next_rep = int(current_time + (next_rep - current_time) * FIVE_YEARS_IN_SECONDS / (next_rep - current_time))
        update_query = "UPDATE cards SET next_rep = ? WHERE id = ?"
        cursor.execute(update_query, (compressed_next_rep, card_id))
        print(f"Compressed card {card_id}: next_rep set to {compressed_next_rep}")

# Commit changes and close the connection
conn.commit()
conn.close()

print("All updates completed.")