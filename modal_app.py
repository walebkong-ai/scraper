import modal
import sys
import json
import logging
import time
from datetime import datetime, timezone

# Define the Modal Stub (App)
app = modal.App("ai-news-dashboard-scraper")

# Define the image with dependencies and local files
# Make sure to include all dependencies needed by the scrapers
scraper_image = (
    modal.Image.debian_slim()
    .pip_install("feedparser", "python-dateutil", "requests")
    .run_commands("mkdir -p /root/.tmp")
    .add_local_dir("tools", remote_path="/root/tools")
)

# A separate function for executing a single scraper.
# By making this a Modal function, we ensure isolated execution in its own container.
# If one scraper crashes due to out-of-memory or a bad segment, it won't kill the orchestrator.
@app.function(
    image=scraper_image,
    timeout=2700  # 45 minute timeout per scraper just to be extra safe
)
def run_single_scraper(name: str):
    """Runs a single scraper synchronouosly."""
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"scraper_{name}")
    
    logger.info(f"▶️ Starting {name} container...")
    start_time = time.time()
    
    # Import here to ensure the local files are mounted in the Modal container
    sys.path.append("/root")
    
    try:
        if name == "bens_bites":
            from tools.scrape_bens_bites import scrape_bens_bites
            data = scrape_bens_bites()
        elif name == "ai_rundown":
            from tools.scrape_ai_rundown import scrape_ai_rundown
            data = scrape_ai_rundown()
        elif name == "cointelegraph":
            from tools.scrape_cointelegraph import scrape_cointelegraph
            data = scrape_cointelegraph()
        elif name == "decrypt":
            from tools.scrape_decrypt import scrape_decrypt
            data = scrape_decrypt()
        elif name == "mckinsey":
            from tools.scrape_mckinsey import scrape_mckinsey
            data = scrape_mckinsey()
        elif name == "hbr":
            from tools.scrape_hbr import scrape_hbr
            data = scrape_hbr()
        elif name == "bain":
            from tools.scrape_bain import scrape_bain
            data = scrape_bain()
        elif name == "bcg":
            from tools.scrape_bcg import scrape_bcg
            data = scrape_bcg()
        else:
            raise ValueError(f"Unknown scraper name: {name}")

        duration = time.time() - start_time
        logger.info(f"✅ {name} finished in {duration:.2f}s. Articles: {len(data.get('articles', []))}")
        return name, data, duration, None

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ {name} failed after {duration:.2f}s: {e}")
        return name, None, duration, str(e)


@app.function(
    image=scraper_image,
    schedule=modal.Period(hours=5), # Run every 5 hours reliably using Modal Cron
    timeout=2700  # 45 minute orchestrator timeout
)
def run_all_scrapers():
    """
    Executes all 6 scrapers using Modal's fan-out capability.
    This guarantees isolated execution per scraper.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("modal_orchestrator")
    
    logger.info("🚀 Starting scheduled scraper run (Modal Container Fan-Out)...")
    start_time = time.time()
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": {},
        "total_articles": 0,
        "errors": [],
        "performance": {}
    }
    
    # List of scrapers to run
    scraper_names = [
        "bens_bites",
        "ai_rundown",
        "cointelegraph",
        "decrypt",
        # "mckinsey", # Disabled due to permanently dead RSS feed causing timeouts
        "hbr",
        "bcg",
        "bain"
    ]
    
    # Fan out execution across multiple Modal containers concurrently
    # This prevents one failing scraper from bringing down the entire run.
    # starmap accepts an iterable of arguments.
    scraper_args = [(name,) for name in scraper_names]
    
    # Note: Use return_exceptions=True so that if the Modal container dies entirely 
    # (e.g., Out Of Memory), starmap won't throw an exception and crash the orchestrator.
    try:
        # map/starmap returns an iterator, we evaluate it to a list to get all results
        scraper_results_raw = list(run_single_scraper.starmap(scraper_args, return_exceptions=True))
    except Exception as e:
         logger.error(f"Failed to fan-out scrapers: {e}")
         results["errors"].append(f"Orchestrator fan-out failed: {e}")
         return results

    # Process results
    for i, res in enumerate(scraper_results_raw):
         name = scraper_names[i]
         
         if isinstance(res, Exception):
              # Container crashed completely (e.g. OOM or Modal system error)
              logger.error(f"Container Exception for {name}: {res}")
              results["errors"].append(f"{name} (Container Crash): {res}")
              results["performance"][name] = "Failed (Container Crash)"
              results["sources"][name] = {
                  "source": name,
                  "articles": [],
                  "success": False,
                  "errors": [str(res)]
              }
              continue
              
         # Standard completion (could be soft error caught by try-except inside the scraper container)
         ret_name, data, duration, error = res
         results["performance"][ret_name] = f"{duration:.2f}s"
         
         if error:
             results["errors"].append(f"{ret_name}: {error}")
             # Add empty result structure for failed sources ensures UI doesn't break
             results["sources"][ret_name] = {
                 "source": ret_name,
                 "articles": [],
                 "success": False,
                 "errors": [error]
             }
         else:
             results["sources"][ret_name] = data
             results["total_articles"] += len(data.get("articles", []))
        
    total_duration = time.time() - start_time
    logger.info(f"🏁 Scrape run complete in {total_duration:.2f}s. Total articles: {results['total_articles']}")
    results["performance"]["total_duration"] = f"{total_duration:.2f}s"
    
    # In a real deployment, we would push 'results' to Supabase here
    # For now, we'll just print them (which logs to Modal dashboard)
    print(json.dumps(results, indent=2))
    
    return results

@app.local_entrypoint()
def main():
    print("Running scrapers locally via Modal...")
    # .remote() executes the function on Modal's servers
    data = run_all_scrapers.remote()
    print(f"Success! Retrieved {data['total_articles']} articles.")
    print(f"Errors: {len(data['errors'])}")
    if data['errors']:
        print("Errors details:", data['errors'])
