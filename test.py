"""
Test script untuk parsing think tags
"""
import re

def remove_think_tags(text: str) -> str:
    """Remove <think>...</think> tags from model output"""
    # Remove think tags and their content
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Clean up extra whitespace
    cleaned = ' '.join(cleaned.split()).strip()
    return cleaned


# Test cases
test_cases = [
    "<think>hmm let me think</think>Hello there!",
    "Hello there!",
    "<think>thinking...</think>Yeah, I can hear you!",
    "Yeah, totally! <think>what should I say</think> That's cool!",
    "<think>internal thought</think>",
    "No think tags here at all",
]

print("=" * 60)
print("TEST: remove_think_tags()")
print("=" * 60)

for i, test in enumerate(test_cases, 1):
    result = remove_think_tags(test)
    print(f"\nTest {i}:")
    print(f"  Input:  '{test}'")
    print(f"  Output: '{result}'")

print("\n" + "=" * 60)
print("TEST: Streaming simulation")
print("=" * 60)

# Simulate streaming tokens
stream_tokens = [
    "<", "think", ">", "hmm", " ", "let", " ", "me", " ", "think", 
    "</", "think", ">", "Hello", " ", "there", "!"
]

print(f"\nTokens: {stream_tokens}")

# Current logic (WRONG)
print("\n--- Current Logic (WRONG) ---")
full_response = ""
in_think_tag = False
output_tokens = []

for token in stream_tokens:
    # Check for think tags
    if '<think>' in token:
        in_think_tag = True
        print(f"  Token '{token}': SKIP (found <think>)")
    elif '</think>' in token:
        in_think_tag = False
        token = token.split('</think>')[-1]
        print(f"  Token after split: '{token}': {'SKIP' if not token else 'SEND'}")
    elif not in_think_tag and '<think>' not in token:
        full_response += token
        output_tokens.append(token)
        print(f"  Token '{token}': SEND")
    else:
        print(f"  Token '{token}': SKIP (in_think_tag={in_think_tag})")

print(f"\nFinal output: '{full_response}'")
print(f"Output tokens: {output_tokens}")

# Better logic
print("\n--- Better Logic ---")
full_response = ""
buffer = ""
in_think = False

for token in stream_tokens:
    buffer += token
    
    # Check if we entered think mode
    if '<think>' in buffer and not in_think:
        # Send everything before <think>
        before_think = buffer.split('<think>')[0]
        if before_think:
            full_response += before_think
            print(f"  Before think: '{before_think}' -> SEND")
        in_think = True
        buffer = ""
        print(f"  Entered think mode")
    
    # Check if we exited think mode
    elif '</think>' in buffer and in_think:
        # Discard everything in think, keep what's after
        after_think = buffer.split('</think>')[-1]
        buffer = after_think
        in_think = False
        print(f"  Exited think mode, buffer now: '{buffer}'")
    
    # If not in think mode and buffer doesn't contain partial tags
    elif not in_think and '<' not in buffer:
        full_response += buffer
        print(f"  Normal text: '{buffer}' -> SEND")
        buffer = ""

# Send remaining buffer if not in think
if buffer and not in_think:
    full_response += buffer
    print(f"  Final buffer: '{buffer}' -> SEND")

print(f"\nFinal output: '{full_response}'")
