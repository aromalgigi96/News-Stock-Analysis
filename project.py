import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import yfinance as yf
import matplotlib.pyplot as plt
from urllib.parse import urljoin

# Base URL for PR Newswire
BASE_URL = "https://www.prnewswire.com"

# Retrieve Detailed Article Content (Helper Function)
def get_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error retrieving article at {url}: {e}")
        return ""
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Trying several selectors for robustness.
    possible_selectors = [
        "div.release-body",
        "div.article-body",
        "div.release-content",
        "article"
    ]
    
    for selector in possible_selectors:
        container = soup.select_one(selector)
        if container:
            paragraphs = container.find_all("p")
            if paragraphs:
                content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                if content:
                    return content
            content = container.get_text(" ", strip=True)
            if content:
                return content
    
    return soup.get_text(" ", strip=True)

# 1. Scan/Parse News Function
def parse_prnewswire_news():
    """
    Downloads the PR Newswire automotive news page and parses news items that are 
    within the last two weeks.
    """
    url = f"{BASE_URL}/news-releases/automotive-transportation-latest-news/automotive-list/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error retrieving news page:", e)
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = []
    
    # Look for news items using a specific CSS selector
    news_items_elements = soup.select("div.row.newsCards > div.card.col-view")
    if not news_items_elements:
        news_items_elements = soup.find_all("a", href=re.compile("/news-releases/"))
        print(f"Fallback: Found {len(news_items_elements)} link candidates.")
    
    today = datetime.now()
    cutoff_date = today - timedelta(days=14)  # Two weeks ago

    for element in news_items_elements:
        try:
            a_tag = element.find("a", href=True)
            if not a_tag:
                continue
            relative_link = a_tag.get("href", "").strip()
            if not relative_link:
                continue
            link = relative_link if relative_link.startswith("http") else urljoin(BASE_URL, relative_link)
            
            # extract headline and publication date from the <h3> element (if available).
            h3_tag = element.find("h3")
            if h3_tag:
                small_tag = h3_tag.find("small")
                time_text = small_tag.get_text(strip=True) if small_tag else ""
                if small_tag:
                    small_tag.decompose()  
                headline = h3_tag.get_text(" ", strip=True)
            else:
                headline = a_tag.get_text(" ", strip=True)
                time_text = ""
            
            # Attempt to parse the publication date from the extracted time_text.
            if time_text:
                pub_date = None
                try:
                    pub_date = datetime.strptime(time_text, "%B %d, %Y")
                except Exception as e:
                    try:
                        pub_date = datetime.strptime(time_text, "%m/%d/%Y")
                    except Exception as e:
                        pub_date = today  
            else:
                pub_date = today
            
            # Skip articles older than the cutoff date.
            if pub_date < cutoff_date:
                continue
            
            # Retrieve detailed article content.
            content = get_article_content(link)
            if not content:
                content = headline  # Fallback if detailed content isn't found.
            
            news_items.append({
                "title": headline,
                "time": time_text,
                "date": pub_date.strftime("%Y-%m-%d"),
                "link": link,
                "content": content
            })
        except Exception as e:
            print("Error parsing a news item:", e)
            continue

    print(f"Parsed {len(news_items)} news items from the last two weeks.")
    return news_items

# 2. Track/Store/Search News

# Define search terms for each ticker symbol.
search_terms = {
    "TSLA": ["TSLA", "Tesla", "NYSE: TSLA", "Nasdaq: TSLA"],
    "GM": ["GM", "General Motors", "NYSE: GM"],
    "F": ["F", "Ford", "NYSE: F"]
}

def find_symbols(text):
    """
    Searches the given text for stock-related keywords.
    """
    found = set()
    for ticker, terms in search_terms.items():
        for term in terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                found.add(ticker)
                break  # Once a match is found for this ticker, move on.
    return list(found)

def store_and_search_news(news_items):

    if not news_items:
        print("No news items found")
        return pd.DataFrame()
    
    df = pd.DataFrame(news_items)
    
    # Apply the enhanced symbol search.
    df["symbols_found"] = df["content"].apply(find_symbols)
    
    csv_filename = "parsed_news.csv"
    df.to_csv(csv_filename, index=False)
    print(f"News items stored in {csv_filename}")
    
    df_with_symbols = df[df["symbols_found"].apply(lambda x: len(x) > 0)]
    if df_with_symbols.empty:
        print("No news items mentioned the selected stock symbols.")
    else:
        print("News items that mentioned selected stock symbols:")
        print(df_with_symbols[["date", "title", "symbols_found"]])
    
    # Display a matrix representation.
    matrix = df[['date', 'title', 'symbols_found']].to_numpy()
    print("\nMatrix representation  (Date, Title, Symbols Found):")
    print(matrix)
    
    return df

# 3. Retrieve Stock Data (Yahoo Finance)
def retrieve_stock_data(symbol, period="30d", interval="1d"):
    """
    Retrieves historical stock data (close price and volume) for the given symbol using yfinance.
    """
    print(f"Retrieving data for {symbol} for the last 30 days...")
    try:
        data = yf.download(symbol, period=period, interval=interval)
        if data.empty:
            print(f"No data found for {symbol}.")
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        print(f"Error retrieving data for {symbol}: {e}")
        return pd.DataFrame()

# 4. Visualize Stock Data
def visualize_stock_data(data, symbol):
    """
    Generates and saves time-series plots for the daily close price and volume.
    """
    if data.empty:
        print(f"No data to plot for {symbol}.")
        return
    
    # Plot daily close price.
    plt.figure(figsize=(10, 6))
    plt.plot(data["Date"], data["Close"], marker='o', linestyle='-')
    plt.title(f"{symbol} Daily Close Price (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    close_filename = f"{symbol}_close_price.png"
    plt.savefig(close_filename)
    plt.show()
    print(f"Close price plot saved as {close_filename}")

    # Plot daily volume.
    plt.figure(figsize=(10, 6))
    plt.plot(data["Date"], data["Volume"], marker='o', linestyle='-', color='orange')
    plt.title(f"{symbol} Daily Volume (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.xticks(rotation=45)
    plt.tight_layout()
    volume_filename = f"{symbol}_volume.png"
    plt.savefig(volume_filename)
    plt.show()
    print(f"Volume plot saved as {volume_filename}")

# 5. Trend Analysis & Recommendation
def analyze_stock_trend(data, symbol):
    """
    Performs trend analysis on the stock's closing prices over 30 days using
    a simple percentage change calculation and returns a recommendation.
    """
    if data.empty:
        print(f"No data available for trend analysis of {symbol}.")
        return None

    # Explicitly convert the close price values to float.
    start_price = float(data["Close"].iloc[0])
    end_price = float(data["Close"].iloc[-1])
    pct_change = (end_price - start_price) / start_price
    print(f"{symbol} start price: {start_price:.2f}, end price: {end_price:.2f}, percentage change: {pct_change:.2%}")

    if pct_change > 0.02:
        recommendation = "BUY STOCK!"
    elif pct_change < -0.02:
        recommendation = "NOT BUY STOCK!"
    else:
        recommendation = "WAIT BEFORE BUYING STOCK!"
    
    # Generate trend plot.
    plt.figure(figsize=(10, 6))
    plt.plot(data["Date"], data["Close"], marker='o', linestyle='-')
    plt.title(f"{symbol} Trend (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    trend_filename = f"{symbol}_trend.png"
    plt.savefig(trend_filename)
    plt.show()
    print(f"Trend plot saved as {trend_filename}")
    
    print(f"Recommendation for {symbol}: {recommendation}")
    return recommendation

# Main Function
def main():
    # Step 1: Parse news from PR Newswire.
    news_items = parse_prnewswire_news()
    if not news_items:
        print("No news items parsed. Exiting.")
        return
    
    # Step 2: Store the news items into a CSV file and search for stock symbols.
    news_df = store_and_search_news(news_items)
    
    # Define the automotive stock symbols for which to retrieve stock data.
    stock_symbols = ["TSLA", "GM", "F"]
    stock_data_dict = {}
    for symbol in stock_symbols:
        data = retrieve_stock_data(symbol, period="30d", interval="1d")
        if not data.empty:
            stock_data_dict[symbol] = data
            visualize_stock_data(data, symbol)
    
    # Step 3: Perform trend analysis for TSLA.
    if "TSLA" in stock_data_dict:
        recommendation = analyze_stock_trend(stock_data_dict["TSLA"], "TSLA")
        with open("TSLA_recommendation.txt", "w") as f:
            f.write(f"Based on the 30-day trend, our recommendation for TSLA is:\n{recommendation}\n")
        print("Recommendation saved to TSLA_recommendation.txt")
    else:
        print("TSLA data not available for trend analysis.")

if __name__ == '__main__':
    main()
