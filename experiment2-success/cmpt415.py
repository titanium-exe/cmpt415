#!/usr/bin/env python3

import requests
import subprocess
import os
import re
import sqlite3
from datetime import datetime

# Configuration constants
API_KEY = "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" 
MODEL = "gpt-4"
P4_FILE = "generated.p4"
OUTPUT_FILE = "build_output.txt"
DB_FILE = "p4_logs.db"
ITERATIONS = 5

def setup_database():
    """Initialize SQLite database to store compilation results."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("old data removed\n")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS p4_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    iteration INTEGER,
                    timestamp TEXT,
                    user_prompt TEXT,
                    generated_code TEXT,
                    compiler_output TEXT,
                    success INTEGER
                 )''')
    conn.commit()
    conn.close()

def log_to_database(iteration, prompt, code, compiler_output, success):
    """Save details of each iteration to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('''INSERT INTO p4_logs (iteration, timestamp, user_prompt, generated_code, compiler_output, success)
                 VALUES (?, ?, ?, ?, ?, ?)''', 
                 (iteration, timestamp, prompt, code, compiler_output, int(success)))
    conn.commit()
    conn.close()

def generate_detailed_prompt(high_level_prompt):
    """Enhance a high-level user input into a detailed, compiler-targeted P4_16 prompt."""
    detailed_prompt = (
        f"{high_level_prompt}. Generate valid P4_16 code that compiles successfully using p4c-bm2-ss. "
        "The code should target a simple switch architecture (e.g., v1model) and include basic packet parsing, "
        "match-action tables, and egress processing. Ensure the code is complete with necessary headers, parsers, "
        "and control blocks."
    )

    print(f"\nDetailed prompt generated: {detailed_prompt}")
    return detailed_prompt

def get_user_prompt():
    """Prompt the user for the high-level intent and generate a detailed version."""
    high_level_prompt = input("Enter your high-level intent for the P4 program: ")
    return generate_detailed_prompt(high_level_prompt)

def generate_p4_code(prompt):
    """Send user intent to OpenAI and retrieve generated P4_16 code."""
    print(f"Generating P4_16 code for intent: {prompt}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert in P4_16 programming. Generate only valid and complete P4 code."},
            {"role": "user", "content": f"Write a P4_16 program for the following intent: {prompt}"}
        ],
        "temperature": 0.3
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    response_data = response.json()

    print("=== RAW RESPONSE START ===")
    print(response.text)
    print("=== RAW RESPONSE END ===")

    if "error" in response_data:
        print("Error from API:")
        print(response_data["error"])
        return None

    try:
        raw_content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("Unexpected response format.")
        return None

    # Extract code block if wrapped in markdown syntax
    code_match = re.search(r"```p4\n([\s\S]*?)\n```", raw_content)
    code = code_match.group(1) if code_match else raw_content

    return code if code.strip() else None

def write_code_to_file(code, filename):
    """Write the generated P4 code to a file."""
    with open(filename, "w") as f:
        f.write(code)
    print(f"Code written to {filename}")

def compile_p4_code(filename):
    """Compile the P4 file using p4c-bm2-ss and capture the result."""
    print("Compiling with p4c-bm2-ss...")
    result = subprocess.run(
        ["p4c-bm2-ss", "--p4v", "16", filename, "-o", "build/compiled.json"],
        capture_output=True, text=True
    )

    compiler_output = result.stdout + result.stderr
    with open(OUTPUT_FILE, "w") as f:
        f.write(compiler_output)

    success = result.returncode == 0

    if success:
        print("Compilation succeeded.")
    else:
        print(f"Compilation failed. Errors saved to {OUTPUT_FILE}.")
        print(result.stderr)

    return compiler_output, success

def fix_p4_code(code, errors):
    """Send compiler errors and code to ChatGPT to attempt automatic fixes."""
    print("Sending compiler errors to ChatGPT for improvement...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert in P4_16 programming and a compiler assistant. Output only corrected, valid P4_16 code that resolves the given errors."},
            {"role": "user", "content": (
                f"The following P4_16 code failed to compile with p4c-bm2-ss:\n\n```p4\n{code}\n```\n\n"
                f"Compiler errors from p4c-bm2-ss:\n{errors}\n\n"
                "Fix the code to resolve these specific errors and ensure it compiles successfully. Return only the corrected P4_16 code."
            )}
        ],
        "temperature": 0.2
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    response_data = response.json()

    if "error" in response_data:
        print("Error from API:")
        print(response_data["error"])
        return None

    try:
        raw_content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("Unexpected response format.")
        return None

    code_match = re.search(r"```p4\n([\s\S]*?)\n```", raw_content)
    fixed_code = code_match.group(1) if code_match else raw_content

    return fixed_code if fixed_code.strip() else None

def summarize_results():
    """Display a summary of success/failure statistics from all iterations."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT iteration, success FROM p4_logs")
    results = c.fetchall()

    total = len(results)
    successes = sum(1 for _, success in results if success)
    failures = total - successes

    print("\n=== Summary ===")
    print(f"Total iterations: {total}")
    print(f"Successful compilations: {successes}")
    print(f"Failed compilations: {failures}")

    if total > 0:
        success_rate = (successes / total) * 100
        print(f"Success rate: {success_rate:.2f}%")

    conn.close()

def write_code_to_file(code, filename):
    """Write the generated P4 code to a file."""
    with open(filename, "w") as f:
        f.write(code)
    print(f"Code written to {filename}")


def main():
    """Main driver loop for iterative code generation and compilation."""
    os.makedirs("build", exist_ok=True)  # Ensure output directory exists
    setup_database()

    user_prompt = get_user_prompt()  # Collect detailed user prompt once

    for iteration in range(1, ITERATIONS + 1):
        print(f"\n=== Iteration {iteration}/{ITERATIONS} ===")
        iteration_filename = f"gen{iteration}.p4"

        code = generate_p4_code(user_prompt)
        if not code:
            log_to_database(iteration, user_prompt, "Failed to generate code", "N/A", False)
            continue

        write_code_to_file(code, iteration_filename)
        compiler_output, success = compile_p4_code(iteration_filename)

        # Log original result
        log_to_database(iteration, user_prompt, code, compiler_output, success)

        # Retry once if compilation fails
        if not success:
            choice = input("Send compiler errors to ChatGPT for improvement? (y/n): ").lower()
            if choice == "y":
                fixed_code = fix_p4_code(code, compiler_output)
                if fixed_code:
                    write_code_to_file(fixed_code, iteration_filename)
                    new_output, new_success = compile_p4_code(iteration_filename)
                    log_to_database(iteration, user_prompt, fixed_code, new_output, new_success)
                else:
                    print("No improved code returned.")


    summarize_results()  # Print final statistics

if __name__ == "__main__":
    main()

