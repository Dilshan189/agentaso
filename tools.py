from crewai.tools import BaseTool
from google_play_scraper import app
from pydantic import BaseModel, Field
from typing import Type

class AppScraperInput(BaseModel):
    app_id: str = Field(description="The exact app ID from the Google Play Store (e.g., 'com.whatsapp').")

class ASOScraperTool(BaseTool):
    name: str = "Scrape App Data"
    description: str = "Scrapes data for a given app ID from the Google Play Store. Useful for getting competitor details like title, description, score, and reviews."
    args_schema: Type[BaseModel] = AppScraperInput

    def _run(self, app_id: str) -> str:
        try:
            result = app(
                app_id,
                lang='en', # default language is 'en'
                country='us' # default country is 'us'
            )
            
            # Extract relevant info
            summary = {
                "title": result.get("title"),
                "summary": result.get("summary"),
                "description": result.get("description"),
                "score": result.get("score"),
                "installs": result.get("installs"),
                "genres": result.get("genres")
            }
            return str(summary)
        except Exception as e:
            return f"Error scraping app {app_id}: {str(e)}"
