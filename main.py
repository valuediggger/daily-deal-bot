import feedparser
import os
import time
import google.generativeai as genai

# --- CONFIGURATION ---
RSS_FEED_URL = "https://news.google.com/rss/search?q=(NBFC+OR+Banking)+AND+(investment+OR+deal+OR+funding+OR+acquisition+OR+merger+OR+stake)&hl=en-IN&gl=IN&ceid=IN:en"

# We try the standard stable models first.
# "gemini-1.5-flash" is the most reliable free tier model.
MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-1.0-pro"
]

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def analyze_market_news():
    print("Fetching NBFC & Banking Deal news...")
    
    feed = feedparser.parse(RSS_FEED_URL)
    headlines = []
    
    for entry in feed.entries[:10]:
        headlines.append(f"- {entry.title}")

    if not headlines:
        print("No specific deal news found today.")
        return

    print(f"Found {len(headlines)} headlines. Sending to AI for analysis...")

    if not API_KEY:
        print("Error: API Key is missing.")
        return

    # --- CONFIGURE THE OLD STABLE SDK ---
    genai.configure(api_key=API_KEY)

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

    success = False
    
    for model_name in MODELS_TO_TRY:
        print(f"Attempting with model: {model_name}...")
        try:
            # Initialize model (Old SDK Style)
            model = genai.GenerativeModel(model_name)
            
            # Generate content
            response = model.generate_content(prompt_text)
            
            # Check if response was blocked
            if not response.parts:
                print(f"Warning: Model {model_name} returned empty response (Safety Filter?).")
                continue

            print("\n" + "="*30)
            print(f"SUCCESS with {model_name}")
            print("="*30)
            print(response.text)
            print("="*30)
            success = True
            break 

        except Exception as e:
            print(f"Failed with {model_name}. Error: {e}")
            print("Switching to next model...\n")
            time.sleep(2) 

    if not success:
        print("CRITICAL: All models failed. Please check your API Key permissions.")

if __name__ == "__main__":
    analyze_market_news()
