import os
import google.generativeai as genai
import logging
from ai_analyst import analyze_stock_with_gemini

# Mock Data
mock_data = {
    "trailingPE": 25.5,
    "forwardPE": 22.1,
    "returnOnEquity": 0.15,
    "debtToEquity": 0.5,
    "profitMargins": 0.12,
    "marketCap": 1000000000,
    "sector": "Energy"
}

# Setup Logging
logging.basicConfig(level=logging.INFO)

def test_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"DEBUG: Found API Key length: {len(api_key) if api_key else 0}")
    
    if not api_key:
        print("ERROR: No API Key found in environment!")
        return

    # print("Attempting to list models...")
    # try:
    #     genai.configure(api_key=api_key)
    #     for m in genai.list_models():
    #         if 'generateContent' in m.supported_generation_methods:
    #             print(f"Model: {m.name}")
    # except Exception as e:
    #     print(f"Listing failed: {e}")

    print("Attempting to call Gemini...")
    result = analyze_stock_with_gemini("TEST_STOCK", mock_data, api_key)
    print("--- Result ---")
    print(result)

if __name__ == "__main__":
    test_ai()
