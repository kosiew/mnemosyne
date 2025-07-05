import sqlite3
import time
import typer
import shutil
from pathlib import Path
from collections import defaultdict

app = typer.Typer()

# Constants
SECONDS_IN_YEAR = 365 * 24 * 60 * 60  # 1 year in seconds
default_db_path = Path.home() / "Library/CloudStorage/OneDrive-Personal/Library/Mnemosyne/default.db"

@app.command()
def compress(
    db_path: Path = typer.Option(default_db_path, help="Path to the database file"),
    years: int = typer.Option(5, help="Maximum number of years to compress next_rep into")
):
    """
    Compress future cards' next_rep to within the next X years (default 5).
    """
    current_time = int(time.time())
    max_next_rep = current_time + years * SECONDS_IN_YEAR

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all cards with their next_rep values
    query = "SELECT id, next_rep FROM cards"
    cursor.execute(query)
    cards = cursor.fetchall()

    # Update next_rep values proportionally
    for card_id, next_rep in cards:
        if next_rep > max_next_rep:
            # Proportionally compress next_rep to within the specified years
            compressed_next_rep = int(
                current_time + (next_rep - current_time) * (max_next_rep - current_time) / (next_rep - current_time)
            )
            update_query = "UPDATE cards SET next_rep = ? WHERE id = ?"
            cursor.execute(update_query, (compressed_next_rep, card_id))
            print(f"Compressed card {card_id}: next_rep set to {compressed_next_rep}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("All updates completed.")

@app.command()
def show_buckets(
    db_path: Path = typer.Option(default_db_path, help="Path to the database file"),
    max_years: int = typer.Option(20, help="Maximum number of years to analyze")
):
    """
    Show the number of cards with next_rep in each future year bucket.
    """
    current_time = int(time.time())

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all cards with their next_rep values
    query = "SELECT next_rep FROM cards"
    cursor.execute(query)
    cards = cursor.fetchall()

    # Create buckets for each year
    buckets = defaultdict(int)
    for (next_rep,) in cards:
        if next_rep > current_time:
            years_ahead = (next_rep - current_time) // SECONDS_IN_YEAR
            buckets[years_ahead] += 1

    # Print the results
    for year in range(max_years + 1):
        print(f"Year {year}: {buckets[year]} cards")

    conn.close()

@app.command()
def backup(
    db_path: Path = typer.Option(default_db_path, help="Path to the database file"),
    backup_path: Path = typer.Option(default_db_path.with_name("default_backup.db"), help="Path to save the backup file")
):
    """
    Backup the database to a specified location.
    """
    shutil.copy(db_path, backup_path)
    print(f"Database backed up to {backup_path}")

if __name__ == "__main__":
    app()