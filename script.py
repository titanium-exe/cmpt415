#!/usr/bin/env python3

import requests
import subprocess
import os
import re
import sqlite3
from datetime import datetime

# Configuration
API_KEY = "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"

MODEL = "gpt-4o"
P4_FILE = "generated.p4"
OUTPUT_FILE = "build_output.txt"
DB_FILE = "p4_logs.db"
MAX_FEEDBACK_ITERATIONS = 4

def setup_database():
    """Reset and initialize SQLite database."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS p4_logs (
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
    print("Database initialized.")

def log_to_database(iteration, prompt, code, compiler_output, success):
    """Log an attempt to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('''
        INSERT INTO p4_logs (iteration, timestamp, user_prompt, generated_code, compiler_output, success)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (iteration, timestamp, prompt, code or "N/A", compiler_output or "N/A", int(success)))
    conn.commit()
    conn.close()

def generate_detailed_prompt(high_level_prompt):
    """Generate detailed prompt including architecture expectations."""
    core_prompt = (
        "Generate valid, complete P4_16 code that compiles with `p4c-bm2-ss` for the `v1model` architecture. "
        "Include all necessary components: header definitions, metadata struct, parser, ingress, egress, "
        "verify checksum, compute checksum, deparser, and the `V1Switch(...) main;` instantiation. "
        "Avoid name conflicts, undefined types, and ensure ports use `bit<9>` type."
    )

    vague_keywords = ["simple", "basic", "something", "anything"]
    if any(word in high_level_prompt.lower() for word in vague_keywords) or len(high_level_prompt.split()) < 5:
        print("Your prompt is too vague. Please clarify.")
        high_level_prompt += " " + input("Provide additional details: ")

    return f"{high_level_prompt}. {core_prompt}"

def get_user_prompt():
    high_level_prompt = input("Enter your P4 intent: ")
    return generate_detailed_prompt(high_level_prompt)

def generate_p4_code(prompt):
    """Call OpenAI API to generate code."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": (
                "You are an expert in P4_16 programming targeting the BMv2 v1model architecture. Your output must "
                "be complete and compile with p4c-bm2-ss. Include headers, metadata, parser, ingress, egress, "
                "verify/compute checksum blocks, deparser, and instantiate the program using V1Switch(...) main;. "
                "Avoid undefined types (e.g., port_t), avoid name reuse, and use bit<9> for ports."
            )},
            {"role": "user", "content": f"Write a P4_16 program for this intent: {prompt}"}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()
        raw_content = response_data["choices"][0]["message"]["content"]
        code_match = re.search(r"```p4\n([\s\S]*?)\n```", raw_content)
        return code_match.group(1).strip() if code_match else raw_content.strip()
    except Exception as e:
        print(f"API error: {e}")
        return None

def write_code_to_file(code, filename):
    with open(filename, "w") as f:
        f.write(code)
    print(f"Code written to {filename}")

def compile_p4_code(filename):
    """Run p4c-bm2-ss and return success + output."""
    result = subprocess.run(
        ["p4c-bm2-ss", "--p4v", "16", filename, "-o", "build/compiled.json"],
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    success = result.returncode == 0
    print("Compilation", "succeeded." if success else "failed.")
    return output, success

def fix_p4_code(code, errors):
    """Send compiler errors + original code back to GPT to request fix."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": (
                "You are a P4 compiler assistant. Fix the provided P4_16 code so that it compiles with p4c-bm2-ss. "
                "Resolve the exact errors given. Do not reuse conflicting names. Always include all required blocks and main instantiation."
            )},
            {"role": "user", "content": (
                f"The following code failed to compile:\n\n```p4\n{code}\n```\n\n"
                f"Compiler errors:\n{errors}\n\n"
                "Please fix and return only the corrected P4_16 code."
            )}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()
        raw_content = response_data["choices"][0]["message"]["content"]
        code_match = re.search(r"```p4\n([\s\S]*?)\n```", raw_content)
        return code_match.group(1).strip() if code_match else raw_content.strip()
    except Exception as e:
        print(f"API error while fixing: {e}")
        return None

def main():
    os.makedirs("build", exist_ok=True)
    setup_database()
    prompt = get_user_prompt()

    iteration = 1
    code = generate_p4_code(prompt)
    if not code:
        log_to_database(iteration, prompt, "N/A", "Failed to generate code", False)
        return

    write_code_to_file(code, P4_FILE)
    output, success = compile_p4_code(P4_FILE)
    log_to_database(iteration, prompt, code, output, success)

    feedback_rounds = 0
    while not success and feedback_rounds < MAX_FEEDBACK_ITERATIONS:
        feedback_rounds += 1
        print(f"Fix attempt {feedback_rounds}...")
        fixed = fix_p4_code(code, output)
        if not fixed:
            break
        write_code_to_file(fixed, P4_FILE)
        output, success = compile_p4_code(P4_FILE)
        log_to_database(iteration, prompt, fixed, output, success)
        code = fixed

    print("\nResult:", "Compilation succeeded." if success else "Still failed after retries.")

if __name__ == "__main__":
    main()
