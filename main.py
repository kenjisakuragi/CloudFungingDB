import logging
from database import init_db, SessionLocal
from scraper_kickstarter import KickstarterScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main execution script for CloudFundingDB scraper.
    """
    logger.info("Initializing database schema...")
    # Initialize tables if they don't exist
    init_db()
    
    # Create DB session
    db = SessionLocal()
    
    try:
        logger.info("Starting Kickstarter Scraper...")
        scraper = KickstarterScraper(db_session=db)
        scraper.run()
        logger.info("Scraping process finished.")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
    except Exception as e:
        logger.critical(f"Unexpected application error: {e}")
    finally:
        db.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    main()
