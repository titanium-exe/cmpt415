#!/usr/bin/env python3

import sqlite3
from collections import Counter
import re

DB_FILE = "p4_logs.db"

def extract_error_messages(compiler_output):
    """Extract key error lines from p4c output, excluding internal debug noise."""
    error_lines = []

    for line in compiler_output.split('\n'):
        stripped = line.strip()

        # Match useful error indicators
        if 'error:' in stripped.lower():
            error_lines.append(stripped)
        elif 'syntax error' in stripped.lower():
            error_lines.append(stripped)
        elif 'invalid' in stripped.lower():
            error_lines.append(stripped)
        elif re.search(r'\bdoes not match declaration\b', stripped, re.IGNORECASE):
            error_lines.append(stripped)
        elif re.search(r'\bundeclared\b|\bmissing\b|\bnot found\b', stripped, re.IGNORECASE):
            error_lines.append(stripped)

    # Clean up: remove duplicates and noisy meta-errors
    filtered = []
    seen = set()
    for err in error_lines:
        if any(skip in err.lower() for skip in ['actual error', 'originating from', 'note:']):
            continue
        if err not in seen:
            filtered.append(err)
            seen.add(err)

    return filtered

def get_most_common_errors(limit=5):
    """Analyze database for most common compilation errors."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT compiler_output FROM p4_logs WHERE success = 0")
    failed_outputs = c.fetchall()
    conn.close()

    all_errors = []
    for output in failed_outputs:
        errors = extract_error_messages(output[0])
        all_errors.extend(errors)

    if not all_errors:
        return []

    error_counts = Counter(all_errors)
    return error_counts.most_common(limit)

def display_error_dashboard():
    """Display a dashboard of most common errors."""
    common_errors = get_most_common_errors()
    print("\n=== Most Common Compilation Errors Dashboard ===")
    if not common_errors:
        print("No errors found in the database.")
        return
    print(f"{'Rank':<5} {'Occurrences':<12} {'Error Message'}")
    print("-" * 80)
    for i, (error, count) in enumerate(common_errors, 1):
        print(f"{i:<5} {count:<12} {error}")

def display_iteration_table():
    """Display a table of results for each iteration."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT iteration, timestamp, user_prompt, success, compiler_output FROM p4_logs")
    results = c.fetchall()
    conn.close()

    if not results:
        print("\nNo iteration data available.")
        return

    print("\n=== Iteration Results Table ===")
    print(f"{'Iteration':<10} {'Timestamp':<25} {'Prompt':<40} {'Success':<8} {'First Error'}")
    print("-" * 120)
    for iteration, timestamp, prompt, success, output in results:
        errors = extract_error_messages(output)
        first_error = errors[0] if errors else "N/A"
        success_str = "Yes" if success else "No"
        # Truncate prompt if too long
        prompt = (prompt[:37] + '...') if len(prompt) > 37 else prompt
        print(f"{iteration:<10} {timestamp:<25} {prompt:<40} {success_str:<8} {first_error}")

def main():
    """Main function to display the dashboard and table."""
    try:
        display_error_dashboard()
        display_iteration_table()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        print("Please ensure the P4 generation script has been run first to populate the database.")

if __name__ == "__main__":
    main()
