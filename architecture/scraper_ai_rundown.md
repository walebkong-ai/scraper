# Architecture SOP: AI Rundown Scraper

## Purpose
Scrape latest articles from The AI Rundown newsletter archive and return structured data conforming to the Article Schema defined in `gemini.md`.

## Input
- None (scraper accesses public URL)

## Output
Conforms to **Scraper Output Schema** from `gemini.md`:
```json
{
  "source": "ai_rundown",
  "scrape_timestamp": "ISO 8601 timestamp",
  "articles": [
    {
      "title": "string",
      "url": "string",
      "published_at": "ISO 8601 timestamp",
      "summary": "string (optional)",
      "author": "string (optional)"
    }
  ],
  "errors": [],
  "success": true
}
```

## Process

### 1. Fetch Archive Page
- URL: `https://www.therundown.ai/archive`
- Method: GET request with User-Agent header
- Store raw HTML in `.tmp/airundown_archive.html` for debugging

### 2. Parse Article List
- Extract all article entries from archive page
- For each article, extract:
  - Title
  - URL
  - Publish date (if available on archive page)
  - Summary/description (if available)

### 3. Fetch Individual Articles (if needed)
- If publish date not on archive page, visit individual articles
- Parse publish date from article metadata
- Extract author if available

### 4. Filter to 24 Hours
- Convert publish dates to ISO 8601 timestamps
- Filter articles where `published_at` is within last 24 hours
- Use current time from system (not scraped time)

### 5. Return Structured Data
- Format as Scraper Output Schema
- Include any errors in `errors` array
- Set `success: false` if critical failure

## Edge Cases

### No New Articles
- Return empty `articles` array
- Set `success: true`
- No errors

### Archive Page Unavailable
- Set `success: false`
- Add error: "Unable to fetch archive page: [HTTP status]"
- Return empty articles array

### Individual Article Fails
- Continue processing other articles
- Add warning to `errors`: "Failed to fetch article: [URL]"
- Omit failed article from results

### Missing Publish Date
- Skip article (don't include in results)
- Add warning: "Article missing publish date: [URL]"

### Rate Limiting
- Implement 1-second delay between individual article requests
- If rate limited (429), add error and stop processing
- Return partial results with `success: false`

## Error Handling
- All errors are non-fatal unless archive page fails
- Log all errors to `.tmp/errors.log`
- Never crash - always return valid JSON

## Dependencies
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `python-dateutil` - Date parsing
- Standard library: `json`, `datetime`, `time`

## Testing Strategy
- Test with current archive page
- Test with simulated 429 rate limit
- Test with missing publish dates
- Verify 24-hour filter logic
- Verify output schema matches `gemini.md`

---

**Last Updated:** 2026-02-15 18:50 EST
