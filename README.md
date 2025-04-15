# 📰 News & Stock Analysis AI – PR Newswire x Yahoo Finance 📈

Ever wondered how headlines impact the stock market?  
This Python-based project helps connect the dots by scanning automotive news articles and checking how they might relate to companies like **Ford (F)**, **General Motors (GM)**, and **Tesla (TSLA)**.

We pull real news stories, check if they mention these big auto stocks, then grab 30 days of price and volume data to see what the market’s doing — and finally, we help answer the big question:  
**Is it time to buy, wait, or stay away?**

---

## 🔍 What This Project Does

Here’s how it works, step by step:

1. **Scrapes automotive news** from PR Newswire (last 2 weeks).
2. **Searches each article** to see if it mentions stock symbols like TSLA, GM, or F.
3. **Uses Yahoo Finance** to pull real stock data for the last 30 days.
4. **Plots clean, colorful charts** for price and volume.
5. **Analyzes stock trends** and recommends one of three actions:  
   → `BUY STOCK!`  
   → `WAIT BEFORE BUYING STOCK!`  
   → `NOT BUY STOCK!`

---

## 📂 Key Features at a Glance

| ✔️ What We Built                  | 💬 What It Does                                                             |
|----------------------------------|------------------------------------------------------------------------------|
| News Scraper                     | Pulls article headlines, dates, and content from PR Newswire                |
| Stock Symbol Scanner             | Finds mentions of TSLA, GM, and F in each article                           |
| CSV Storage                      | Saves all parsed news and matches neatly into a `.csv` file                 |
| Stock Data Fetching              | Uses `yfinance` to pull 30-day price/volume data for each stock             |
| Charting & Visualization         | Creates simple, readable charts using `matplotlib`                          |
| Matrix Representation            | Builds a table showing which articles mention which stocks                 |
| Trend Analyzer & Recommendation  | Makes a call: is the stock going up, down, or all over the place?           |





