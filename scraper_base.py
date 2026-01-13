from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from models import Project
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectData(BaseModel):
    """Pydantic model for data validation before database insertion."""
    platform_name: str
    project_id_on_platform: str
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    current_amount: Optional[float] = None
    target_amount: Optional[float] = None
    currency: Optional[str] = None
    backers_count: Optional[int] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class BaseScraper(ABC):
    def __init__(self, db_session: Session):
        self.db = db_session

    def run(self):
        """Standard execution flow."""
        logger.info(f"Starting scraper: {self.__class__.__name__}")
        try:
            projects = self.fetch_projects()
            if projects:
                self.save_to_db(projects)
            else:
                logger.info("No projects found to save.")
            logger.info("Scraping completed successfully.")
        except Exception as e:
            logger.error(f"Scraper failed: {e}")


    @abstractmethod
    def fetch_projects(self) -> List[ProjectData]:
        """Scrapes projects from the platform."""
        pass

    def save_to_db(self, projects: List[ProjectData]):
        """
        Saves a list of project data to the database using an upsert operation.
        Updates existing records if (platform_name, project_id_on_platform) conflicts.
        """
        if not projects:
            logger.info("No projects to save.")
            return

        # Prepare data for bulk insert/upsert
        projects_dicts = [p.model_dump() for p in projects]
        
        # Add scraped_at timestamp
        for p in projects_dicts:
            p['scraped_at'] = datetime.utcnow()

        # Construct SQLAlchemy Insert statement
        stmt = insert(Project).values(projects_dicts)

        # Define the upsert logic (ON CONFLICT DO UPDATE)
        # We want to update fields that might change over time
        update_dict = {
            'title': stmt.excluded.title,
            'url': stmt.excluded.url,
            'thumbnail_url': stmt.excluded.thumbnail_url,
            'current_amount': stmt.excluded.current_amount,
            'target_amount': stmt.excluded.target_amount,
            'currency': stmt.excluded.currency,
            'backers_count': stmt.excluded.backers_count,
            'end_date': stmt.excluded.end_date,
            'description': stmt.excluded.description,
            'scraped_at': stmt.excluded.scraped_at
        }

        # Do the upsert
        # Constraint name matches the one defined in models.py
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['platform_name', 'project_id_on_platform'],
            set_=update_dict
        )

        try:
            self.db.execute(upsert_stmt)
            self.db.commit()
            logger.info(f"Successfully upserted {len(projects)} projects.")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving projects to database: {e}")
            raise
