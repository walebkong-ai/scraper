#!/usr/bin/env python3
"""
Test suite for newsletter scrapers
Validates output against schemas defined in gemini.md
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List


def validate_scraper_output_schema(output: Dict) -> List[str]:
    """Validate output matches Scraper Output Schema from gemini.md"""
    errors = []
    
    # Check required top-level fields
    required_fields = ["source", "scrape_timestamp", "articles", "errors", "success"]
    for field in required_fields:
        if field not in output:
            errors.append(f"Missing required field: {field}")
    
    # Validate source
    if "source" in output:
        valid_sources = ["bens_bites", "ai_rundown", "reddit", "twitter"]
        if output["source"] not in valid_sources:
            errors.append(f"Invalid source: {output['source']}")
    
    # Validate scrape_timestamp is ISO 8601
    if "scrape_timestamp" in output:
        try:
            datetime.fromisoformat(output["scrape_timestamp"].replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"Invalid scrape_timestamp format: {output['scrape_timestamp']}")
    
    # Validate articles is a list
    if "articles" in output:
        if not isinstance(output["articles"], list):
            errors.append("articles must be a list")
        else:
            # Validate each article
            for i, article in enumerate(output["articles"]):
                article_errors = validate_article(article, i)
                errors.extend(article_errors)
    
    # Validate errors is a list
    if "errors" in output:
        if not isinstance(output["errors"], list):
            errors.append("errors must be a list")
    
    # Validate success is boolean
    if "success" in output:
        if not isinstance(output["success"], bool):
            errors.append("success must be a boolean")
    
    return errors


def validate_article(article: Dict, index: int) -> List[str]:
    """Validate individual article schema"""
    errors = []
    prefix = f"Article {index}"
    
    # Check required fields
    required_fields = ["title", "url", "published_at"]
    for field in required_fields:
        if field not in article:
            errors.append(f"{prefix}: Missing required field: {field}")
    
    # Validate title is string
    if "title" in article and not isinstance(article["title"], str):
        errors.append(f"{prefix}: title must be a string")
    
    # Validate url is string and starts with http
    if "url" in article:
        if not isinstance(article["url"], str):
            errors.append(f"{prefix}: url must be a string")
        elif not article["url"].startswith("http"):
            errors.append(f"{prefix}: url must be absolute (start with http)")
    
    # Validate published_at is ISO 8601
    if "published_at" in article:
        try:
            datetime.fromisoformat(article["published_at"].replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{prefix}: Invalid published_at format: {article['published_at']}")
    
    return errors


def validate_24h_filter(output: Dict) -> List[str]:
    """Validate all articles are within last 24 hours"""
    errors = []
    
    if "articles" not in output:
        return errors
    
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    
    for i, article in enumerate(output["articles"]):
        if "published_at" not in article:
            continue
        
        try:
            pub_date = datetime.fromisoformat(article["published_at"].replace("Z", "+00:00"))
            if pub_date < cutoff:
                errors.append(f"Article {i} is older than 24 hours: {article['published_at']}")
            if pub_date > now:
                errors.append(f"Article {i} is in the future: {article['published_at']}")
        except ValueError:
            # Already caught by schema validation
            pass
    
    return errors


def test_scraper(scraper_name: str, output: Dict) -> bool:
    """Test a scraper output"""
    print(f"\n{'='*60}")
    print(f"Testing {scraper_name}")
    print(f"{'='*60}\n")
    
    all_errors = []
    
    # Schema validation
    print("1. Validating schema...")
    schema_errors = validate_scraper_output_schema(output)
    if schema_errors:
        all_errors.extend(schema_errors)
        print(f"   ❌ Schema validation failed:")
        for error in schema_errors:
            print(f"      - {error}")
    else:
        print("   ✅ Schema validation passed")
    
    # 24-hour filter validation
    print("\n2. Validating 24-hour filter...")
    filter_errors = validate_24h_filter(output)
    if filter_errors:
        all_errors.extend(filter_errors)
        print(f"   ❌ 24-hour filter validation failed:")
        for error in filter_errors:
            print(f"      - {error}")
    else:
        print("   ✅ 24-hour filter validation passed")
    
    # Summary
    print(f"\n3. Summary:")
    print(f"   Source: {output.get('source', 'N/A')}")
    print(f"   Success: {output.get('success', 'N/A')}")
    print(f"   Articles found: {len(output.get('articles', []))}")
    print(f"   Errors reported: {len(output.get('errors', []))}")
    
    if output.get("errors"):
        print(f"   Scraper errors:")
        for error in output["errors"]:
            print(f"      - {error}")
    
    # Final result
    if all_errors:
        print(f"\n❌ TEST FAILED: {len(all_errors)} validation errors")
        return False
    else:
        print(f"\n✅ TEST PASSED")
        return True


def main():
    """Run all tests"""
    print("="*60)
    print("SCRAPER TEST SUITE")
    print("="*60)
    
    # Test files (will be generated by running scrapers)
    test_files = [
        ("Ben's Bites", "../.tmp/bensbites_output.json"),
        ("AI Rundown", "../.tmp/airundown_output.json")
    ]
    
    results = []
    for name, filepath in test_files:
        try:
            with open(filepath, "r") as f:
                output = json.load(f)
            passed = test_scraper(name, output)
            results.append((name, passed))
        except FileNotFoundError:
            print(f"\n⚠️  Skipping {name}: Output file not found ({filepath})")
            print("   Run the scraper first to generate test data")
            results.append((name, None))
        except json.JSONDecodeError as e:
            print(f"\n❌ {name}: Invalid JSON in output file")
            print(f"   Error: {e}")
            results.append((name, False))
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for name, passed in results:
        if passed is None:
            print(f"⚠️  {name}: SKIPPED")
        elif passed:
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED")
    
    # Exit code
    if all(p is not False for _, p in results):
        print("\n✅ All tests passed or skipped")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
