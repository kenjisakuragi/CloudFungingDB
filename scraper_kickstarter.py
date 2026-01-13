import json
import logging
from typing import List
from datetime import datetime
from playwright.sync_api import sync_playwright
from scraper_base import BaseScraper, ProjectData

logger = logging.getLogger(__name__)

class KickstarterScraper(BaseScraper):
    BASE_URL = "https://www.kickstarter.com/discover/advanced?sort=magic"

    def fetch_projects(self) -> List[ProjectData]:
        projects_data = []
        
        with sync_playwright() as p:
            # Launch browser
            # Headless mode is usually preferred for scrapers
            browser = p.chromium.launch(headless=True)
            # Create a context with a standard user agent to avoid basic blocks
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = context.new_page()
            
            try:
                logger.info(f"Navigating to {self.BASE_URL}")
                page.goto(self.BASE_URL, timeout=60000)
                
                # Wait for the project cards to ensure content is loaded
                # Using the selector for the data attribute itself
                page.wait_for_selector('[data-project]', timeout=30000)
                
                # Allow a small buffer for dynamic content to settle if needed
                page.wait_for_timeout(2000)
                
                # Get all project elements
                cards = page.query_selector_all('[data-project]')
                logger.info(f"Found {len(cards)} project cards.")
                
                for card in cards:
                    try:
                        raw_json = card.get_attribute('data-project')
                        if not raw_json:
                            continue
                            
                        data = json.loads(raw_json)
                        
                        # Handle Date Parsing
                        # Kickstarter usually provides 'deadline' as a Unix timestamp (seconds)
                        end_date = None
                        if 'deadline' in data:
                            end_date = datetime.utcfromtimestamp(data['deadline'])
                        
                        # Extract URLs
                        project_url = ""
                        if 'urls' in data and 'web' in data['urls']:
                            project_url = data['urls']['web']['project']
                            
                        thumbnail_url = None
                        if 'photo' in data and 'full' in data['photo']:
                            thumbnail_url = data['photo']['full']

                        # Create ProjectData object
                        project = ProjectData(
                            platform_name='Kickstarter',
                            project_id_on_platform=str(data.get('id')),
                            title=data.get('name', 'Unknown Title'),
                            url=project_url,
                            thumbnail_url=thumbnail_url,
                            current_amount=float(data.get('pledged', 0)),
                            target_amount=float(data.get('goal', 0)),
                            currency=data.get('currency'),
                            backers_count=int(data.get('backers_count', 0)),
                            end_date=end_date,
                            description=data.get('blurb')
                        )
                        projects_data.append(project)

                    except KeyError as e:
                        logger.warning(f"Missing key in Kickstarter data: {e}")
                    except Exception as e:
                        logger.warning(f"Failed to parse project card: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error during scraping or navigation: {e}")
                
            finally:
                browser.close()
                
        return projects_data
