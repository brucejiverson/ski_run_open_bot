from __future__ import annotations

# All the things that define a ski run
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger('ski-bot.ski_run')


class RunStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    UNKNOWN = "Unknown"


class Difficulty(IntEnum):
    GREEN = 1
    BLUE = 2
    BLACK = 3
    DOUBLEBLACK = 4
    TRIPLEBLACK = 5
    

@dataclass
class SkiRunData:
    """A simple data class to describe a ski run. Note that the name of the run is not included here because it is the key in the dictionary that holds the SkiRunData."""
    difficulty: Difficulty
    status: RunStatus = RunStatus.UNKNOWN
    mountain_section: str | None = None
    
    @classmethod
    def get_as_dict_of_strings(cls, instance:SkiRunData) -> Dict[str, str]:
        return {
            'difficulty': instance.difficulty.value if instance.difficulty else None,
            'status': instance.status.value if instance.status else None,
            'mountain_section': instance.mountain_section
        }
        
    @classmethod
    def build_from_dict_of_strings(cls, data:Dict[str, str]) -> SkiRunData:
        difficulty = None if data['difficulty'] is None else Difficulty(data['difficulty'])
        status = None if data['status'] is None else RunStatus(data['status'])
        return SkiRunData(
            difficulty,
            status,
            data['mountain_section']
        )


@dataclass
class SkiRunScrapeData:
    timestamp: float
    resort: str
    run_data: Dict[str, SkiRunData] # run names are the key workds the SkiRunData is the values

    def get_as_raw_dict(self) -> Dict[str, Any]:
        """Returns a dictionary that can be serialized to JSON."""
        
        # turn the ski runs into a dict for json niceness
        my_dict:Dict[str, Any] = {
            'timestamp': self.timestamp,
            'resort': self.resort
        }
        my_dict['run_data'] = {}
        for run_name, run_info in self.run_data.items():
            my_dict['run_data'][run_name] = SkiRunData.get_as_dict_of_strings(run_info)
        return my_dict
    
    @classmethod
    def build_from_raw_dict(cls, data:Dict[str, Any]) -> SkiRunScrapeData:
        """Builds a SkiRunScrapeData object from a dictionary that was serialized from JSON."""
        
        run_data = {}
        for run_name, run_info in data['run_data'].items():
            run_data[run_name] = SkiRunData.build_from_dict_of_strings(run_info)
        return SkiRunScrapeData(
            data['timestamp'],
            data['resort'],
            run_data
        )


def filter_for_opened_runs(
    current_resort_data: Dict[str, SkiRunData], 
    prior_ski_run_info: Dict[str, SkiRunData],
    minimum_difficulty:Difficulty = Difficulty.BLACK
    ) -> Dict[str, SkiRunData]:
    """Takes two lists of ski runs, old and current, and returns a list containing the runs that have opened.
    
    Parameters:
        current_ski_run_info (List[ski_run.SkiRun]): A list of ski runs with the current status
        prior_ski_run_info (List[ski_run.SkiRun]): A list of ski runs with the previous status
        
    Returns:
        changed_status (List[ski_run.SkiRun]): A list of ski runs that have changed status
    """
    
    changed_statuses = {}
    for run_name, run in current_resort_data.items():
        old_run = prior_ski_run_info[run_name]
        
        run_is_open = run.status == RunStatus.OPEN
        run_used_to_be_closed = old_run.status == RunStatus.CLOSED
        run_meets_minimum_difficulty = run.difficulty.value >= minimum_difficulty.value
        
        if run_is_open and run_used_to_be_closed and run_meets_minimum_difficulty:
            changed_statuses[run_name] = run
    
    return changed_statuses


def save_resort_run_status_to_file(run_data:SkiRunScrapeData, file_name_override:str = None):
    """Save the current run status to a file for later use.
    
    Args:
            resort (str): The name of the resort
            run_statuses (List[SkiRunData]): A list of ski runs current information
            timestamp (float): The time the data was scraped
    """
            
    raw = run_data.get_as_raw_dict()
    path = f'./data/{run_data.resort}'
    if file_name_override:
        path += f'_{file_name_override}'
    else: 
        path += '_run_status.json'
        
    with open(path, 'w') as file:
        json.dump(raw, file, indent=4)
            
            
def load_resort_run_data_from_file(resort:str, file_name_override:str = None) -> SkiRunScrapeData:
    """Load the current run status from a file.
        
    Args:
            resort (str): The name of the resort
            file_name_override (str): The name of the file to load. If not provided, the default file name is used.
    
    Returns:
            run_statuses (SkiRunScrapeData): A list of ski runs current information
    """
    
    
    if file_name_override:
        path = f'./data/{resort}_{file_name_override}'
    else:
        path = f'./data/{resort}_run_status.json'
    
    with open(path, 'r') as file:
        read_dict:Dict[str, Dict] = json.load(file)
        
    return SkiRunScrapeData.build_from_raw_dict(read_dict)
    