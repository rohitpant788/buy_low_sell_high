import google.generativeai as genai
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def analyze_stock_with_gemini(symbol, fundamental_data, api_key):
    """
    Analyzes stock fundamentals using Google Gemini model.
    """
    if not api_key:
        return "⚠️ Please provide a Gemini API Key in the sidebar to use AI features."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest') # Using Gemini Flash Latest

        # Construct Prompt
        metrics_str = json.dumps(fundamental_data, indent=2)
        prompt = f"""
        Act as a professional financial analyst. I will provide you with fundamental data for a stock.
        
        Stock Symbol: {symbol}
        Data:
        {metrics_str}

        Please analyze this data and provide:
        1. A brief "Fundamental Strength" summary (3-4 bullet points).
        2. Key Risks (if any).
        3. A "Value Verdict": [Undervalued / Fairly Valued / Overvalued] based on P/E, P/B vs general industry standards.
        
        Keep it concise and actionable for a trader looking for breakout candidates.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        logger.error(f"Gemini AI Error: {str(e)}")
        return f"❌ AI Analysis Failed: {str(e)}"
