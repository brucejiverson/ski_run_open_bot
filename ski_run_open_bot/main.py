from __future__ import annotations
from typing import List, Dict, Callable

import tweepy
import time
import logging
import os
from datetime import datetime

import ski_run
from ski_run_open_bot.solitude_utah import scrape_ski_run_information
# build a twitter bot to send out a tweet when a ski run opens

# set up the bot with tweepy
logger = logging.getLogger('ski-bot.twitter')


def create_twitter_client() -> tweepy.API:
    """Connects to the Twitter API using environment variables.
    
    Borrowed from RealPython."""
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api
             

def send_tweet(twitter_api: tweepy.API, recently_opened_runs: Dict[str, ski_run.SkiRunData]):
    """"""
    for run_name, opened_run in recently_opened_runs.items():
        logger.info(f'Detected that {opened_run.name} has opened. Sending tweet.')
        
        tweet = 'Opened_run ({}) at {} has opened!'.format(
            opened_run.name, 
            opened_run.difficulty.name
        )
        
        tweepy_api.update_status(tweet)
              
                
def monitor_for_run_status_change_and_take_action(resort:str, scrape_function: Callable, action_function: Callable, action_args=[], check_period_minute:int=20):
    """Periodically calls the scrape function which should return a SkiRunScrapeData, filters for recently opened runs, and calls action function passing the recently opened runs as a parameter.
    
    Parameters:
        scrape_function: a function that returns a SkiRunScrapeData with up to date information
        action_function: a function that takes a dict of [str, SkiRunData] as a parameter
        action_args: a list of arguments to pass to the action function
    """
    
    # check to load the ski runs from file
    prior_resort_data = None
    try:
        prior_resort_data = ski_run.load_resort_run_data_from_file(resort)
    except FileNotFoundError:
        logger.info(f'No file found for resort {resort}. File will be created.')
        
    
    while 1:
        # load the ski runs
        new_data:ski_run.SkiRunScrapeData = scrape_function()
        # ski_run.save_resort_run_status_to_file(new_data)
        
        if prior_resort_data: # this if statement should skip the check 
            recently_opened_runs = ski_run.filter_for_opened_runs(new_data.run_data, prior_resort_data.run_data)
            
            for run_name, run_info in recently_opened_runs.items():
                logger.info('{} run ({}) was opened!'.format(run_name, run_info.difficulty.name))
            
            action_function(recently_opened_runs, *action_args)
        
        # save the new data
        ski_run.save_resort_run_status_to_file(new_data)
        
        prior_resort_data = new_data
        time.sleep(60*check_period_minute)
        

if __name__ == "__main__":
    
    def do_nothing(opened):pass
    
    # tweepy_api = create_twitter_client()
    monitor_for_run_status_change_and_take_action(
        'solitude',
        scrape_ski_run_information, 
        # send_tweet, 
        # [tweepy_api]
        do_nothing,
        )