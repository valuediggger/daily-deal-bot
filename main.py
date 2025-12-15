import feedparser
import os
from google import genai

# --- CONFIGURATION ---
# 1. SPECIALIZED SEARCH QUERY
# We search specifically for NBFC/Banking + keywords like "invest", "raise", "deal", "acquire"
# "hl=en-IN&gl=IN" focuses on India news where the term "NBFC" is most relevant. 
# If you want global news, change to "hl=en-US&gl=US".
RSS_FEED_URL = "https://news.google.com/rss/search?q=(NBFC+OR+Banking)+AND+(investment+OR+deal+OR+funding+OR+acquisition+OR+merger+OR+stake)&hl=en-IN&gl=IN&ceid=IN:en"

API_KEY = os.environ.get("GOOGLE_API_KEY")

def analyze_market_news():
    print("Fetching NBFC & Banking Deal news...")
    
    # 2. Parse the RSS Feed
    feed = feedparser.parse(RSS_FEED_URL)
    headlines = []
    
    # Collect top 10 relevant headlines
    # We add the link so you can click it later if needed (optional)
    for entry in feed.entries[:10]:
        headlines.append(f"- {entry.title}")

    if not headlines:
        print("No specific deal news found today.")
        return

    print(f"Found {len(headlines)} headlines. Sending to AI for analysis...")

    # 3. Initialize Gemini
    if not API_KEY:
        print("Error: GOOGLE_API_KEY is missing.")
        return

    try:
        client = genai.Client(api_key=API_KEY)

        # 4. The Analysis Prompt
        # We ask the AI to filter strictly for financial deals/investments
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

        response = client.models.generate_content(
            model="gemini-1.5-flash",
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
