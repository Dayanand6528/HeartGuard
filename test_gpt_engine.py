import chatbot_engine

test_queries = [
    "BP 150/95",
    "my sugar is 180 mg/dl",
    "cholesterol 250",
    "spo2 91%",
    "pulse 120 bpm",
    "how to reduce my blood pressure",
    "what is fever paracetamol dose",
    "how to reduce stress and panic attack",
    "sleep hygiene and insomnia",
    "acid reflux vs heart attack",
    "stroke FAST warning signs"
]

print("=== TESTING MEDICAL GPT ENGINE WITH VARIOUS INPUTS ===")
for q in test_queries:
    resp = chatbot_engine.get_bot_response(q)
    clean_resp = resp.encode('ascii', 'ignore').decode('utf-8')
    print(f"\nQUERY: '{q}'")
    print(clean_resp[:250] + "...")
    print("-" * 50)

print("\nAll GPT Engine input tests completed successfully!")
