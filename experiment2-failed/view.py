#!/usr/bin/env python3

import sqlite3

DB_FILE = "p4_logs.db"

def view_first_and_last_rows():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Get first row
    c.execute("SELECT * FROM p4_logs ORDER BY id ASC LIMIT 1")
    first_row = c.fetchone()

    # Get last row
    c.execute("SELECT * FROM p4_logs ORDER BY id DESC LIMIT 1")
    last_row = c.fetchone()

    conn.close()

    def print_row(row, label):
        if row:
            print("=" * 80)
            print(f"{label} (Log ID: {row[0]})")
            print(f"Iteration: {row[1]}")
            print(f"Timestamp: {row[2]}")
            print(f"Success: {'Yes' if row[6] else 'No'}")
            print("\n--- User Prompt ---")
            print(row[3])
            print("\n--- Generated P4 Code ---")
            print(row[4])
            print("\n--- Compiler Output ---")
            print(row[5])
            print("=" * 80 + "\n")
        else:
            print(f"{label} not found.\n")

    print_row(first_row, "First Entry")
    if last_row and last_row[0] != first_row[0]:
        print_row(last_row, "Last Entry")

if __name__ == "__main__":
    view_first_and_last_rows()
