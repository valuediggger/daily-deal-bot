import feedparser
import os
import time
from google import genai
from google.genai import types

# --- CONFIGURATION ---
RSS_FEED_URL = "https://news.google.com/rss/search?q=(NBFC+OR+Banking)+AND+(investment+OR+deal+OR+funding+OR+acquisition+OR+merger+OR+stake)&hl=en-IN&gl=IN&ceid=IN:en"

# Priority list of models to try. 
# It tries the fast/cheap ones first. If they fail (404 or 429), it moves to the next.
MODELS_TO_TRY = [
    "gemini-1.5-flash",       # Standard fast model
    "gemini-1.5-flash-8b",    # High-volume, smaller model (very likely to work if others fail)
    "gemini-2.0-flash-exp",   # Experimental 2.0
    "gemini-1.5-pro",         # heavier model (fallback)
    "gemini-1.0-pro"          # Oldest fallback
]

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def analyze_market_news():
    print("Fetching NBFC & Banking Deal news...")
    
    feed = feedparser.parse(RSS_FEED_URL)
    headlines = []
    
    # Collect top 10 relevant headlines
    for entry in feed.entries[:10]:
        headlines.append(f"- {entry.title}")

    if not headlines:
        print("No specific deal news found today.")
        return

    print(f"Found {len(headlines)} headlines. Sending to AI for analysis...")

    if not API_KEY:
        print("Error: API Key is missing.")
        return

    client = genai.Client(api_key=API_KEY)

    prompt_text = (
        "You are a financial analyst. Review these news headlines about NBFCs and Banking.\n"
        "Identify and summarize ONLY:\n"
        "1. New Investments (Who invested in whom?)\n"
        "2. Mergers & Acquisitions (Deals)\n"
        "3. Major Regulatory Updates affecting the sector\n\n"
        "Headlines:\n"
        + "\n".join(headlines) + "\n\n"
        "Output Format:\n"
        "- **Deals & Investments:** [List details]\n"
        "- **Top Sector News:** [Major non-deal updates]\n"
        "If nothing relevant is found in a category, write 'None'."
    )

    # --- THE LOOP: TRY MODELS UNTIL ONE WORKS ---
    success = False
    
    for model_name in MODELS_TO_TRY:
        print(f"Attempting with model: {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt_text
            )
            
            # If we get here, it worked!
            print("\n" + "="*30)
            print(f"SUCCESS with {model_name}")
            print("="*30)
            print(response.text)
            print("="*30)
            success = True
            break # Stop looping

        except Exception as e:
            # If it's a 429 (Quota) or 404 (Not Found), we print and try the next one.
            print(f"Failed with {model_name}. Error: {e}")
            print("Switching to next model...\n")
            time.sleep(1) # Short pause before next try

    if not success:
        print("CRITICAL: All models failed. Please check your API Key permissions or Quota.")

if __name__ == "__main__":
    analyze_market_news()
