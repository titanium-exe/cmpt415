#!/usr/bin/env python3

import requests
import subprocess
import os
import re
import sqlite3
from datetime import datetime
import pandas as pd

# Configuration constants
API_KEY = "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"
MODEL = "gpt-3.5-turbo"  # Updated to a widely available model
DB_FILE = "p4_logs.db"

def summarize_from_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM p4_logs", conn)
        conn.close()
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return

    if df.empty:
        print("Database is empty. No logs to summarize.")
        return

    df['result'] = df['success'].map({1: 'Success', 0: 'Failure'})
    # Updated regex to capture full error message until newline or end
    df['error_type'] = df['compiler_output'].str.extract(r'error: (.*?)(?:\n|$)', expand=False).fillna('Unknown')

    total = len(df)
    successes = df['success'].sum()
    failures = total - successes
    latest_code = df.iloc[-1]['generated_code']

    error_summary = df[df['success'] == 0]['error_type'].value_counts().head(5)
    max_error = error_summary.idxmax() if not error_summary.empty else "None"
    max_count = error_summary.max() if not error_summary.empty else 0

    report = (
        f"Performance Report (Generated from Database):\n"
        f"--------------------------------------------------\n"
        f"Total Attempts: {total}\n"
        f"Successes: {successes}\n"
        f"Failures: {failures}\n"
        f"Success Rate: {successes/total*100:.2f}%\n"
        f"\nMost Frequent Compiler Error: '{max_error}' ({max_count} times)\n"
        f"\nLast Generated Code:\n\n{latest_code[:1000]}...\n\n"
    )

    print(report)

    # Send report to ChatGPT for feedback
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a P4 code reviewer. Evaluate the compilation results."},
            {"role": "user", "content": report + "\nWas the code improving? What suggestions do you have based on these logs?"}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        print("\nChatGPT Feedback:")
        print(content)
    except Exception as e:
        print(f"Error getting ChatGPT feedback: {e}")

if __name__ == "__main__":
    summarize_from_db()