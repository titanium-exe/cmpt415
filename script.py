#!/usr/bin/env python3

import requests
import subprocess
import os
import re
import sqlite3
from datetime import datetime

# Configuration constants
API_KEY = "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"
MODEL = "gpt-3.5-turbo"  # Updated to a commonly available model
P4_FILE = "generated.p4"
OUTPUT_FILE = "build_output.txt"
DB_FILE = "p4_logs.db"
MAX_FEEDBACK_ITERATIONS = 10
ITERATIONS = 15  # Reintroduced loop

def setup_database():
    """Reset and initialize a fresh SQLite database."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # Wipe old DB if it exists

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
    print("Database reset and initialized.")

def log_to_database(iteration, prompt, code, compiler_output, success):
    """Log iteration results into the SQLite database with error handling."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute('''INSERT INTO p4_logs (iteration, timestamp, user_prompt, generated_code, compiler_output, success)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (iteration, timestamp, prompt, code or "N/A", compiler_output or "N/A", int(success)))
        conn.commit()
        print(f"Logged iteration {iteration} to database: success={success}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def generate_detailed_prompt(high_level_prompt):
    """Expand the user's high-level intent into a detailed, compiler-compatible P4_16 prompt."""
    architecture_details = (
        "Generate valid P4_16 code that compiles successfully using p4c-bm2-ss. "
        "Use the v1model architecture for BMv2. The code must include complete definitions for headers, parsers, "
        "match-action tables, ingress, egress, checksum verification, and deparser. "
        "Always use the full 6-parameter V1Switch instantiation: Parser, VerifyChecksum, Ingress, Egress, "
        "ComputeChecksum, and Deparser. Ensure all control blocks use correct signatures, port values are bit<9>, "
        "and avoid undefined types or name conflicts."
    )

    vague_keywords = ["simple", "basic", "something", "anything"]
    is_vague = any(keyword in high_level_prompt.lower() for keyword in vague_keywords) or len(high_level_prompt.split()) < 5

    if is_vague:
        print("\n=== Simulated ChatGPT Response ===")
        print(f"Your prompt: '{high_level_prompt}' is too high-level. Please provide more specifics.")
        more_details = input("Please provide additional details: ")
        high_level_prompt += f" {more_details}"

    detailed_prompt = f"{high_level_prompt}. {architecture_details}"
    print(f"\nDetailed prompt generated: {detailed_prompt}")
    return detailed_prompt

def get_user_prompt():
    high_level_prompt = input("Enter your high-level intent for the P4 program: ")
    return generate_detailed_prompt(high_level_prompt)

def generate_p4_code(prompt):
    print(f"Generating P4_16 code for intent: {prompt}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert in P4_16 programming. Generate valid P4_16 code that compiles with p4c-bm2-ss. Avoid naming conflicts, use correct V1Switch arguments, and use bit<9> for port types."},
            {"role": "user", "content": f"Write a P4_16 program for the following intent: {prompt}"}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return None

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
    code = code_match.group(1) if code_match else raw_content
    return code.strip() if code else None

def write_code_to_file(code, filename):
    with open(filename, "w") as f:
        f.write(code)
    print(f"Code written to {filename}")

def compile_p4_code(filename):
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
    print("Sending compiler errors to ChatGPT for improvement...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert in P4_16 programming and a compiler assistant. Generate corrected code that resolves the errors. Avoid reusing names and undefined types like port_t. Ensure correct V1Switch usage."},
            {"role": "user", "content": (
                f"The following P4_16 code failed to compile with p4c-bm2-ss:\n\n```p4\n{code}\n```\n\n"
                f"Compiler errors from p4c-bm2-ss:\n{errors}\n\n"
                "Fix the code to resolve these specific errors and ensure it compiles successfully. Return only the corrected P4_16 code."
            )}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return None

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
    return fixed_code.strip() if fixed_code else None

def main():
    os.makedirs("build", exist_ok=True)
    setup_database()

    user_prompt = get_user_prompt()

    for iteration in range(1, ITERATIONS + 1):
        print(f"\n=== Iteration {iteration}/{ITERATIONS} ===")
        
        code = generate_p4_code(user_prompt)
        if not code:
            log_to_database(iteration, user_prompt, "Failed to generate code", "N/A", False)
            continue

        write_code_to_file(code, P4_FILE)
        compiler_output, success = compile_p4_code(P4_FILE)
        log_to_database(iteration, user_prompt, code, compiler_output, success)

        feedback_rounds = 0
        while not success and feedback_rounds < MAX_FEEDBACK_ITERATIONS:
            feedback_rounds += 1
            print(f"Attempting fix #{feedback_rounds}...")
            fixed_code = fix_p4_code(code, compiler_output)
            if not fixed_code:
                log_to_database(iteration, user_prompt, code, "No improved code returned", False)
                break

            write_code_to_file(fixed_code, P4_FILE)
            compiler_output, success = compile_p4_code(P4_FILE)
            log_to_database(iteration, user_prompt, fixed_code, compiler_output, success)
            code = fixed_code

        if not success:
            print(f"Iteration {iteration} failed to compile after {MAX_FEEDBACK_ITERATIONS} attempts.")
        else:
            print(f"Iteration {iteration} compiled successfully!")

if __name__ == "__main__":
    main()