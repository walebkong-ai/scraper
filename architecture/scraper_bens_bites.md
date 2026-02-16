# Architecture SOP: Ben's Bites Scraper

## Purpose
Scrape latest articles from Ben's Bites newsletter archive and return structured data conforming to the Article Schema defined in `gemini.md`.

## Input
- None (scraper accesses public URL)

## Output
Conforms to **Scraper Output Schema** from `gemini.md`:
```json
{
  "source": "bens_bites",
  "scrape_timestamp": "ISO 8601 timestamp",
  "articles": [
    {
      "title": "string",
      "url": "string",
      "published_at": "ISO 8601 timestamp",
      "summary": "string (subtitle/description)",
      "author": "Ben Tossell"
    }
  ],
  "errors": [],
  "success": true
}
```

## Process

### 1. Fetch Archive Page
- URL: `https://www.bensbites.com/archive`
- Method: GET request with User-Agent header
- Store raw HTML in `.tmp/bensbites_archive.html` for debugging

### 2. Parse Article Links
- Extract all article links matching pattern `/p/*`
- Extract title and subtitle for each article
- Build list of article URLs

### 3. Fetch Individual Articles (for dates)
- For each article URL, fetch the page
- Parse publish date from article metadata or content
- Extract author if available (default: "Ben Tossell")

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
