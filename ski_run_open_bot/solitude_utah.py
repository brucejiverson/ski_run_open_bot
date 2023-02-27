import ski_run_open_bot.ski_run as ski_run
from ski_run_open_bot.util import parse_element_to_match_enum

from typing import List, Dict, Any
import time
import logging

from bs4 import BeautifulSoup
import dryscrape


logger = logging.getLogger('ski-bot.solitude')

url = 'https://www.solitudemountain.com/mountain-and-village/conditions-and-maps#/'
# url = "https://v2.mtnfeed.com/solitude#/"


def scrape_ski_run_information() -> ski_run.SkiRunScrapeData:
    """Retrieve up to date information from the Solitude website about all ski runs.
    
    Returns:
            scraped_data (Dict): A dictionary containing the timestamp and a list of ski runs
    """
    
    logger.debug(f'Initializing dryscrape session for {url}')
    # use dryscrape to load the page (should work with javascript)
    sess = dryscrape.Session()
    sess.visit(url)
    response:str = sess.body()
    soup = BeautifulSoup(response, "lxml")
    mountain_areas = soup.find_all('div', class_= 'mountain-area')

    ski_runs:Dict[str, ski_run.SkiRunData] = {}
    for area_element in mountain_areas:
        mountain_area_name:str = area_element.find("h1", class_="area-name ttu").text
        ski_run_elements:BeautifulSoup = area_element.find_all("div", class_="trail col no-stretch keep-padding expandable")
        
        for ski_run_element in ski_run_elements:
            name = ski_run_element.find("div", class_="trail-name").text
            difficulty = parse_element_to_match_enum(ski_run_element, ski_run.Difficulty)
            run_status = parse_element_to_match_enum(ski_run_element, ski_run.RunStatus)
            
            run = ski_run.SkiRunData(
                name,
                difficulty,
                run_status,
                mountain_area_name
            )
            logger.debug("Found run: " + str(run))
            ski_runs[name] = run
    logger.info(f'Found a total of {len(ski_runs)} runs at Solitude')
    return ski_run.SkiRunScrapeData(time.monotonic(), 'solitude', ski_runs)


