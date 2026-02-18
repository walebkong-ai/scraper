import modal
import sys
import json
import logging
import asyncio
import time
from datetime import datetime, timezone

# Define the Modal Stub (App)
app = modal.App("ai-news-dashboard-scraper")

# Define the image with dependencies and local files
scraper_image = (
    modal.Image.debian_slim()
    .pip_install("feedparser", "python-dateutil", "requests")
    .run_commands("mkdir -p /root/.tmp")
    .add_local_dir("tools", remote_path="/root/tools")
)

@app.function(
    image=scraper_image,
    schedule=modal.Period(hours=18),
    timeout=1800  # 30 minute timeout
)
async def run_all_scrapers():
    """
    Executes all 6 scrapers and aggregates the results in parallel.
    Runs every 18 hours.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("modal_orchestrator")
    
    logger.info("🚀 Starting scheduled scraper run (Parallel Execution)...")
    start_time = time.time()
    
    # We import here to ensure the local files are mounted and available
    sys.path.append("/root")
    
    try:
        from tools.scrape_bens_bites import scrape_bens_bites
        from tools.scrape_ai_rundown import scrape_ai_rundown
        from tools.scrape_cointelegraph import scrape_cointelegraph
        from tools.scrape_decrypt import scrape_decrypt
        from tools.scrape_mckinsey import scrape_mckinsey
        from tools.scrape_hbr import scrape_hbr
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources": {},
            "total_articles": 0,
            "errors": [],
            "performance": {}
        }
        
        async def run_scraper(name, func):
            """Helper to run a synchronous scraper in a thread and track performance."""
            t0 = time.time()
            logger.info(f"▶️ Starting {name}...")
            try:
                # Run synchronous function in a separate thread to avoid blocking the loop
                data = await asyncio.to_thread(func)
                duration = time.time() - t0
                logger.info(f"✅ {name} finished in {duration:.2f}s. Articles: {len(data.get('articles', []))}")
                return name, data, duration, None
            except Exception as e:
                duration = time.time() - t0
                logger.error(f"❌ {name} failed after {duration:.2f}s: {e}")
                return name, None, duration, str(e)

        # List of scrapers to run
        scrapers = [
            ("bens_bites", scrape_bens_bites),
            ("ai_rundown", scrape_ai_rundown),
            ("cointelegraph", scrape_cointelegraph),
            ("decrypt", scrape_decrypt),
            ("mckinsey", scrape_mckinsey),
            ("hbr", scrape_hbr)
        ]
        
        # Execute all scrapers in parallel
        tasks = [run_scraper(name, func) for name, func in scrapers]
        scraper_results = await asyncio.gather(*tasks)
        
        # Process results
        for name, data, duration, error in scraper_results:
            results["performance"][name] = f"{duration:.2f}s"
            
            if error:
                results["errors"].append(f"{name}: {error}")
                # Add empty result structure for failed sources ensures UI doesn't break
                results["sources"][name] = {
                    "source": name,
                    "articles": [],
                    "success": False,
                    "errors": [error]
                }
            else:
                results["sources"][name] = data
                results["total_articles"] += len(data.get("articles", []))
            
        total_duration = time.time() - start_time
        logger.info(f"🏁 Scrape run complete in {total_duration:.2f}s. Total articles: {results['total_articles']}")
        results["performance"]["total_duration"] = f"{total_duration:.2f}s"
        
        # In a real deployment, we would push 'results' to Supabase here
        # For now, we'll just print them (which logs to Modal dashboard)
        print(json.dumps(results, indent=2))
        
        return results
        
    except ImportError as e:
        logger.error(f"Import Error: {e}")
        # List files to debug mounting
        import os
        logger.error(f"Files in /root/tools: {os.listdir('/root/tools')}")
        raise

@app.local_entrypoint()
def main():
    print("Running scrapers locally via Modal...")
    # .remote() on an async function returns a coroutine-like object that waits for result
    data = run_all_scrapers.remote()
    print(f"Success! Retrieved {data['total_articles']} articles.")
    print(f"Errors: {len(data['errors'])}")
    if data['errors']:
        print("Errors details:", data['errors'])
