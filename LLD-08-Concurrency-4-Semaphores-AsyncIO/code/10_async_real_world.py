"""
Real-World Async: Web Scraper with Rate Limiting
=================================================
Fetch 15 pages concurrently, but limit to 4 at a time
using asyncio.Semaphore. Process results as they arrive.
"""

import asyncio
import time
import random

# Simulated web pages with different response times
PAGES = [
    ("https://example.com/page/1", 0.5),
    ("https://example.com/page/2", 1.2),
    ("https://example.com/page/3", 0.3),
    ("https://example.com/page/4", 0.8),
    ("https://example.com/page/5", 1.5),
    ("https://example.com/page/6", 0.4),
    ("https://example.com/page/7", 0.9),
    ("https://example.com/page/8", 0.6),
    ("https://example.com/page/9", 1.0),
    ("https://example.com/page/10", 0.7),
    ("https://example.com/page/11", 1.1),
    ("https://example.com/page/12", 0.2),
    ("https://example.com/page/13", 0.8),
    ("https://example.com/page/14", 1.3),
    ("https://example.com/page/15", 0.5),
]

MAX_CONCURRENT = 4
sem = asyncio.Semaphore(MAX_CONCURRENT)

async def fetch_page(url, delay):
    """Fetch a page with rate limiting."""
    async with sem:
        print(f"  [{time.strftime('%H:%M:%S')}] Fetching {url}...")
        await asyncio.sleep(delay)  # Simulate network request
        word_count = random.randint(100, 2000)
        print(f"  [{time.strftime('%H:%M:%S')}] Got {url} ({word_count} words)")
        return {"url": url, "words": word_count, "time": delay}

async def scrape_all():
    """Fetch all pages concurrently (limited by semaphore)."""
    tasks = [fetch_page(url, delay) for url, delay in PAGES]
    results = await asyncio.gather(*tasks)
    return results

print(f"Async Web Scraper")
print(f"Pages: {len(PAGES)}")
print(f"Max concurrent: {MAX_CONCURRENT}")
print(f"=" * 50)

start = time.time()
results = asyncio.run(scrape_all())
elapsed = time.time() - start

total_words = sum(r["words"] for r in results)
total_sequential = sum(delay for _, delay in PAGES)

print(f"\n--- Results ---")
print(f"Pages scraped:    {len(results)}")
print(f"Total words:      {total_words}")
print(f"Actual time:      {elapsed:.1f}s")
print(f"Sequential would: {total_sequential:.1f}s")
print(f"Speedup:          {total_sequential / elapsed:.1f}x faster")
print(f"\nSemaphore kept us to {MAX_CONCURRENT} connections at a time.")
print(f"Polite scraping without overwhelming the server!")
