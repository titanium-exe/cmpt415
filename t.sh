

API_KEY="to be put here."
MODEL="gpt-4"
P4_FILE="generated.p4"
OUTPUT_FILE="build_output.txt"

read -p "Enter your intent for the P4 program: " USER_PROMPT

echo "Generating P4_16 code from ChatGPT..."

RESPONSE=$(curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "model": "$MODEL",
  "messages": [
    {"role": "system", "content": "You are an expert in P4_16 programming. Generate only valid and complete P4 code."},
    {"role": "user", "content": "Write a P4_16 program for the following intent: $USER_PROMPT"}
  ],
  "temperature": 0.3
}
EOF
)

echo "=== RAW RESPONSE START ==="
echo "$RESPONSE"
echo "=== RAW RESPONSE END ==="

# Check for error in response
if echo "$RESPONSE" | grep -q '"error"'; then
    echo "Error from API:"
    echo "$RESPONSE" | jq '.error'
    exit 1
fi

RAW_CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')

# Check for empty or null content
if [[ "$RAW_CONTENT" == "null" || -z "$RAW_CONTENT" ]]; then
    echo "No response content from ChatGPT. Exiting."
    exit 1
fi

# Try to extract code block
CODE=$(echo "$RAW_CONTENT" | sed -n '/```p4/,/```/p' | sed '1d;$d')

# If no code block, use entire content
if [[ -z "$CODE" ]]; then
    CODE="$RAW_CONTENT"
fi

# Final check
if [[ "$CODE" == "null" || -z "$CODE" ]]; then
    echo "No code was generated. Exiting."
    exit 1
fi

echo "$CODE" > "$P4_FILE"
echo "Code written to $P4_FILE"

echo "Compiling with p4c-bm2-ss..."
p4c-bm2-ss --p4v 16 "$P4_FILE" -o build/compiled.json &> "$OUTPUT_FILE"

if [[ $? -eq 0 ]]; then
    echo "Compilation succeeded."
else
    echo "Compilation failed. Errors saved to $OUTPUT_FILE."
    cat "$OUTPUT_FILE"
fi

read -p "Send compiler errors to ChatGPT for improvement? (y/n): " CHOICE

if [[ "$CHOICE" == "y" ]]; then
    ERRORS=$(<"$OUTPUT_FILE")

    IMPROVED=$(curl -s https://api.openai.com/v1/chat/completions \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d @- <<EOF
{
  "model": "$MODEL",
  "messages": [
    {"role": "system", "content": "You're a P4_16 compiler assistant. Output only corrected P4 code."},
    {"role": "user", "content": "This P4_16 code failed to compile:\n$CODE\n\nCompiler errors:\n$ERRORS\n\nPlease fix the code and return valid P4_16."}
  ],
  "temperature": 0.2
}
EOF
    )

    FIXED=$(echo "$IMPROVED" | jq -r '.choices[0].message.content' | sed -n '/```p4/,/```/p' | sed '1d;$d')
    if [[ -z "$FIXED" ]]; then
        FIXED=$(echo "$IMPROVED" | jq -r '.choices[0].message.content')
    fi

    if [[ -n "$FIXED" ]]; then
        echo "$FIXED" > "$P4_FILE"
        echo "Fixed code written to $P4_FILE. Recompiling..."
        p4c-bm2-ss --p4v 16 "$P4_FILE" -o build/compiled_fixed.json &> "$OUTPUT_FILE"
        cat "$OUTPUT_FILE"
    else
        echo "No improved code returned."
    fi
fi

