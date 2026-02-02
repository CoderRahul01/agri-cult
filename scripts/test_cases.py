import requests
import json
import time

BASE_URL = "http://localhost:8000"

TEST_CASES = [
    {
        "name": "Disease Intent - Yellow Patches",
        "question": "My citrus leaves are showing yellow blotchy patches. What could this be?"
    },
    {
        "name": "Disease Intent - Prevention",
        "question": "How do I prevent Citrus Canker in my orchard?"
    },
    {
        "name": "Disease Intent - Whitefly",
        "question": "What treatment should I use for whitefly infestation on my citrus trees?"
    },
    {
        "name": "Scheme Intent - Andhra Pradesh",
        "question": "What government schemes are available for citrus farmers in Andhra Pradesh?"
    },
    {
        "name": "Scheme Intent - Drip Subsidy",
        "question": "Are there any subsidies for setting up drip irrigation in my citrus farm?"
    },
    {
        "name": "Scheme Intent - Organic Farming",
        "question": "How can I get financial help to start organic citrus farming?"
    },
    {
        "name": "Hybrid Intent - Citrus Greening",
        "question": "What government schemes can help me manage Citrus Greening disease in my farm?"
    },
    {
        "name": "Hybrid Intent - Equipment & Funding",
        "question": "I need help with pest control equipment and funding. What options do I have?"
    },
    {
        "name": "Hybrid Intent - Drip & Root Disease",
        "question": "Can I get government support for setting up drip irrigation to prevent root diseases?"
    },
    {
        "name": "Edge Case - Out of Scope",
        "question": "Who is the Prime Minister of India?"
    },
    {
        "name": "Edge Case - Spelling Mistake",
        "question": "How to treat citrs cancr?"
    },
    {
        "name": "Self-Learning - New Topic",
        "question": "What are the latest 2024 export regulations for organic Nagpur oranges?"
    }
]

def test_feedback():
    print("\n📝 Testing Feedback Loop...")
    payload = {
        "question": "How to grow dragon fruit in citrus soil?",
        "is_satisfied": False,
        "correct_info": "Dragon fruit can be grown in well-drained citrus soil with a pH of 6-7."
    }
    response = requests.post(f"{BASE_URL}/feedback", json=payload)
    if response.status_code == 200:
        print(f"✅ Feedback Success: {response.json()['message']}")
    else:
        print(f"❌ Feedback Failed: {response.text}")

def run_tests():
    print(f"🚀 Starting verification tests for {len(TEST_CASES)} cases...")
    
    results = []
    
    for case in TEST_CASES:
        print(f"\n📝 Testing: {case['name']}")
        print(f"❓ Question: {case['question']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/query",
                json={"question": case["question"]},
                timeout=120
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success ({elapsed:.2f}s)")
                print(f"🎯 Intent: {data.get('intent')}")
                print(f"💬 Answer: {data.get('answer')[:150]}...")
                results.append({"name": case["name"], "status": "PASS", "intent": data.get("intent")})
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                results.append({"name": case["name"], "status": "FAIL"})
                
        except Exception as e:
            print(f"💥 Error: {str(e)}")
            results.append({"name": case["name"], "status": "ERROR"})
            
    print("\n" + "="*50)
    print("📊 FINAL TEST REPORT")
    print("="*50)
    for r in results:
        print(f"[{r['status']}] {r['name']} (Intent: {r.get('intent', 'N/A')})")
    print("="*50)
    
    # Run feedback test at the end
    test_feedback()

if __name__ == "__main__":
    # Note: Ensure the FastAPI app is running before executing this
    run_tests()
