import sqlite3
import pandas as pd

# Load data
conn = sqlite3.connect('p4_logs.db')
df = pd.read_sql_query("SELECT * FROM p4_logs", conn)
conn.close()

# Basic summary of all iterations
print("=" * 80)
print("P4 COMPILATION RUN SUMMARY")
print("=" * 80)
print(df[['iteration', 'timestamp', 'success']].to_string(index=False))
print()

# Extract error types using regex
df['error_type'] = df['compiler_output'].str.extract(r'error: ([^:]+):', expand=False)

# Get top 3 most common error types
top_errors = df['error_type'].value_counts().head(3)

print("=" * 80)
print("TOP COMPILER ERRORS WITH EXAMPLES")
print("=" * 80)

for error_type, count in top_errors.items():
    print("\n" + "-" * 80)
    print(f"ERROR TYPE: {error_type.upper()} ({count} occurrences)")
    print("-" * 80)

    # Get one sample of this error type
    sample = df[df['error_type'] == error_type]['compiler_output'].dropna().iloc[0]
    print(sample.strip())

print("\n" + "=" * 80)
print("End of Report")
print("=" * 80)

