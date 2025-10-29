"""
Test script untuk fetch streaming dari LM Studio
"""
import requests
import json

LM_STUDIO_URL = "http://10.42.100.159:1234/v1/chat/completions"

# Test 1: Tanpa /no_think
print("=" * 70)
print("TEST 1: Tanpa /no_think")
print("=" * 70)

messages_without = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Keep responses short."
    },
    {
        "role": "user",
        "content": "Hello, can you hear me?"
    }
]

print(f"\n📤 Sending to: {LM_STUDIO_URL}")
print(f"📦 Messages: {json.dumps(messages_without, indent=2)}")
print("\n🔄 Streaming response:")
print("-" * 70)

try:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "qwen3-0.6b",
            "messages": messages_without,
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": True
        },
        stream=True,
        timeout=15
    )
    
    full_text = ""
    token_count = 0
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_text += content
                            token_count += 1
                            print(f"Token {token_count}: '{content}'")
                except json.JSONDecodeError:
                    pass
    
    print("-" * 70)
    print(f"\n✅ Complete!")
    print(f"📊 Total tokens: {token_count}")
    print(f"📝 Full text: '{full_text}'")
    
except Exception as e:
    print(f"❌ Error: {e}")


# Test 2: Dengan /no_think di user message
print("\n\n" + "=" * 70)
print("TEST 2: Dengan /no_think di user message")
print("=" * 70)

messages_with_user = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Keep responses short."
    },
    {
        "role": "user",
        "content": "/no_think Hello, can you hear me?"
    }
]

print(f"\n📤 Sending to: {LM_STUDIO_URL}")
print(f"📦 Messages: {json.dumps(messages_with_user, indent=2)}")
print("\n🔄 Streaming response:")
print("-" * 70)

try:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "qwen3-0.6b",
            "messages": messages_with_user,
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": True
        },
        stream=True,
        timeout=15
    )
    
    full_text = ""
    token_count = 0
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_text += content
                            token_count += 1
                            print(f"Token {token_count}: '{content}'")
                except json.JSONDecodeError:
                    pass
    
    print("-" * 70)
    print(f"\n✅ Complete!")
    print(f"📊 Total tokens: {token_count}")
    print(f"📝 Full text: '{full_text}'")
    
except Exception as e:
    print(f"❌ Error: {e}")


# Test 3: Dengan /no_think di system message
print("\n\n" + "=" * 70)
print("TEST 3: Dengan /no_think di system message")
print("=" * 70)

messages_with_system = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Keep responses short.\n/no_think"
    },
    {
        "role": "user",
        "content": "Hello, can you hear me?"
    }
]

print(f"\n📤 Sending to: {LM_STUDIO_URL}")
print(f"📦 Messages: {json.dumps(messages_with_system, indent=2)}")
print("\n🔄 Streaming response:")
print("-" * 70)

try:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "qwen3-0.6b",
            "messages": messages_with_system,
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": True
        },
        stream=True,
        timeout=15
    )
    
    full_text = ""
    token_count = 0
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_text += content
                            token_count += 1
                            print(f"Token {token_count}: '{content}'")
                except json.JSONDecodeError:
                    pass
    
    print("-" * 70)
    print(f"\n✅ Complete!")
    print(f"📊 Total tokens: {token_count}")
    print(f"📝 Full text: '{full_text}'")
    
except Exception as e:
    print(f"❌ Error: {e}")


# Test 4: Dengan instruksi "RESPOND IMMEDIATELY"
print("\n\n" + "=" * 70)
print("TEST 4: Dengan instruksi 'RESPOND IMMEDIATELY'")
print("=" * 70)

messages_immediate = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Keep responses short.\nRESPOND IMMEDIATELY. Do NOT think first, just answer directly."
    },
    {
        "role": "user",
        "content": "Hello, can you hear me?"
    }
]

print(f"\n📤 Sending to: {LM_STUDIO_URL}")
print(f"📦 Messages: {json.dumps(messages_immediate, indent=2)}")
print("\n🔄 Streaming response:")
print("-" * 70)

try:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "qwen3-0.6b",
            "messages": messages_immediate,
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": True
        },
        stream=True,
        timeout=15
    )
    
    full_text = ""
    token_count = 0
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_text += content
                            token_count += 1
                            print(f"Token {token_count}: '{content}'")
                except json.JSONDecodeError:
                    pass
    
    print("-" * 70)
    print(f"\n✅ Complete!")
    print(f"📊 Total tokens: {token_count}")
    print(f"📝 Full text: '{full_text}'")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("Lihat output di atas untuk melihat perbedaan antara:")
print("1. Tanpa /no_think")
print("2. Dengan /no_think di user message")
print("3. Dengan /no_think di system message")
print("4. Dengan instruksi 'RESPOND IMMEDIATELY'")
