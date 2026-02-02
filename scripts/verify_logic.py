import requests
import json

BASE_URL = "http://localhost:8000"

def test_query(name, question):
    print(f"\n--- TESTING: {name} ---")
    print(f"❓ Question: {question}")
    
    response = requests.post(
        f"{BASE_URL}/query",
        json={"question": question},
        timeout=120
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"🎯 Intent: {data['intent']}")
        print(f"💬 Answer: {data['answer'][:200]}...")
        print(f"📚 Sources: {[s['document'] for s in data['sources']]}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Case 1: Information is in PDF (Citrus Canker symptoms)
    test_query("Info in PDF", "What are the first visible signs of Citrus Canker on leaves?")
    
    # Case 2: Information is NOT in PDF (2025 subsidies - will likely require search)
    test_query("Info likely NOT in PDF", "Are there any new 2025 specific subsidies for drip irrigation in Maharashtra finalized yet?")
