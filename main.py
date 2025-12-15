import feedparser
import os
from google import genai

# --- CONFIGURATION ---
RSS_FEED_URL = "https://news.google.com/rss/search?q=(NBFC+OR+Banking)+AND+(investment+OR+deal+OR+funding+OR+acquisition+OR+merger+OR+stake)&hl=en-IN&gl=IN&ceid=IN:en"

# The SDK will automatically look for 'GOOGLE_API_KEY' or 'GEMINI_API_KEY'
# But we capture it here just to check if it exists before running.
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def analyze_market_news():
    print("Fetching NBFC & Banking Deal news...")
    
    # 1. Parse the RSS Feed
    feed = feedparser.parse(RSS_FEED_URL)
    headlines = []
    
    # Collect top 10 relevant headlines
    for entry in feed.entries[:10]:
        headlines.append(f"- {entry.title}")

    if not headlines:
        print("No specific deal news found today.")
        return

    print(f"Found {len(headlines)} headlines. Sending to AI for analysis...")

    # 2. Check Key
    if not API_KEY:
        print("Error: API Key (GEMINI_API_KEY or GOOGLE_API_KEY) is missing.")
        return

    try:
        # 3. Initialize Client (New SDK Style)
        client = genai.Client(api_key=API_KEY)

        prompt = (
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

        # 4. Generate Content using the NEW Model
        # UPDATED: Changed from 'gemini-1.5-flash' to 'gemini-2.0-flash'
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )

        print("\n" + "="*30)
        print("NBFC & BANKING INTELLIGENCE")
        print("="*30)
        print(response.text)
        print("="*30)

    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    analyze_market_news()
