import sqlite3
import time
import typer
import shutil
from pathlib import Path
from collections import defaultdict

app = typer.Typer()

# Constants
SECONDS_IN_YEAR = 365 * 24 * 60 * 60  # 1 year in seconds
SECONDS_IN_DAY = 24 * 60 * 60  # 1 day in seconds
default_db_path = Path.home() / "Library/CloudStorage/OneDrive-Personal/Library/Mnemosyne/default.db"

@app.command()
def compress(
    db_path: Path = typer.Option(default=default_db_path, help="Path to the database file"),
    years: int = typer.Option(5, help="Maximum number of years to compress next_rep into")
):
    """
    Compress future cards' next_rep to within the next X years (default 5).
    A backup is created before compressing.
    """
    # Call the backup command before compressing
    backup(db_path=db_path, backups_folder=db_path.parent / "backups")

    current_time = int(time.time())
    max_next_rep = current_time + years * SECONDS_IN_YEAR

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all cards with their next_rep values
    query = "SELECT id, next_rep FROM cards"
    cursor.execute(query)
    cards = cursor.fetchall()

    # Filter cards with next_rep more than max_next_rep
    future_cards = [(card_id, next_rep) for card_id, next_rep in cards if next_rep > max_next_rep]

    if future_cards:
        # Calculate the range for evenly distributing next_rep values
        start_time = current_time + SECONDS_IN_DAY  # Start from tomorrow
        end_time = max_next_rep
        total_days = (end_time - start_time) // (24 * 60 * 60)

        # Evenly distribute next_rep values
        for index, (card_id, _) in enumerate(future_cards):
            allocated_next_rep = start_time + (index * (total_days * 24 * 60 * 60) // len(future_cards))
            update_query = "UPDATE cards SET next_rep = ?, easiness = ? WHERE id = ?"
            cursor.execute(update_query, (allocated_next_rep, 1.3, card_id))
            print(f"Allocated card {card_id}: next_rep set to {allocated_next_rep}, easiness set to 1.3")

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

    # Print the results (only buckets with cards)
    for year in sorted(buckets.keys()):
        if year <= max_years:
            print(f"Year {year}: {buckets[year]} cards")

    conn.close()

@app.command()
def extract_cards_by_tag(
    db_path: Path = typer.Option(default=default_db_path, help="Path to the database file"),
    tag: str = typer.Option(..., help="Tag name to filter cards by"),
    output_file: Path = typer.Option(None, help="Optional output CSV file path")
):
    """
    Extract all cards that have the specified tag.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Support full tag name matching (stored in tags.name)
    cursor.execute("select _id from tags where name=?", (tag,))
    tag_row = cursor.fetchone()
    if not tag_row:
        print(f"No tag found with name '{tag}'")
        conn.close()
        return

    tag_id = tag_row[0]
    query = """
    select cards.* from cards
    join tags_for_card on cards._id=tags_for_card._card_id
    where tags_for_card._tag_id=?
    """
    cursor.execute(query, (tag_id,))
    rows = cursor.fetchall()

    if not rows:
        print(f"No cards found for tag '{tag}'")
        conn.close()
        return

    # Print to stdout
    column_names = [description[0] for description in cursor.description]
    print(",".join(column_names))
    for row in rows:
        formatted = []
        for item in row:
            if item is None:
                formatted.append("")
            else:
                formatted.append(str(item).replace('"', '""'))
        print(",".join(formatted))

    # Optionally save to CSV
    if output_file is not None:
        output_file = output_file.expanduser()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(",".join(column_names) + "\n")
            for row in rows:
                formatted = []
                for item in row:
                    if item is None:
                        formatted.append("")
                    else:
                        # Quote values that contain commas or newlines
                        text = str(item)
                        if "," in text or "\n" in text or '"' in text:
                            text = '"' + text.replace('"', '""') + '"'
                        formatted.append(text)
                f.write(",".join(formatted) + "\n")
        print(f"Exported {len(rows)} cards to {output_file}")

    conn.close()

@app.command()
def backup(
    db_path: Path = typer.Option(default_db_path, help="Path to the database file"),
    backups_folder: Path = typer.Option(default_db_path.parent / "backups", help="Path to the backups folder")
):
    """
    Backup the database to the backups folder with a timestamp.
    """
    backups_folder.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_path = backups_folder / f"{db_path.stem}-{timestamp}.db"
    shutil.copy(db_path, backup_path)
    print(f"Database backed up to {backup_path}")

@app.command()
def restore_backup(
    db_path: Path = typer.Option(default_db_path, help="Path to the database file"),
    backups_folder: Path = typer.Option(default_db_path.parent / "backups", help="Path to the backups folder")
):
    """
    Restore the database from the latest backup in the backups folder and remove the backup file.
    """
    backup_files = sorted(backups_folder.glob(f"{db_path.stem}-*.db"), reverse=True)
    if not backup_files:
        print("No backups found to restore.")
        return
    latest_backup = backup_files[0]
    shutil.copy(latest_backup, db_path)
    print(f"Database restored from {latest_backup} to {db_path}")

    # Remove the backup file
    latest_backup.unlink()
    print(f"Backup file {latest_backup} has been removed.")

if __name__ == "__main__":
    app()