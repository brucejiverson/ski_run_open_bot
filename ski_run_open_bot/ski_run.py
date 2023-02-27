from __future__ import annotations

# All the things that define a ski run
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Dict
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
    DOUBLE_BLACK = 4
    TRIPLE_BLACK = 5
    

@dataclass
class SkiRunData:
    name:str
    difficulty: Difficulty
    status: RunStatus = RunStatus.UNKNOWN
    mountain_section: str | None = None
    
    @classmethod
    def get_as_dict_of_strings(cls, instance:SkiRunData) -> Dict[str, str]:
        return {
            'name': instance.name,
            'difficulty': instance.difficulty.value if instance.difficulty else None,
            'status': instance.status.value if instance.status else None,
            'mountain_section': instance.mountain_section
        }
        
    @classmethod
    def build_from_dict_of_strings(cls, data:Dict[str, str]) -> SkiRunData:
        difficulty = None if data['difficulty'] is None else Difficulty(data['difficulty'])
        status = None if data['status'] is None else RunStatus(data['status'])
        return SkiRunData(
            data['name'],
            difficulty,
            status,
            data['mountain_section']
        )


@dataclass
class SkiRunScrapeData:
    timestamp: float
    resort: str
    run_data: Dict[str, SkiRunData] # run names are the key workds the SkiRunData is the values


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


def save_resort_run_status_to_file(run_data:SkiRunScrapeData):
    """Save the current run status to a file for later use.
    
    Args:
            resort (str): The name of the resort
            run_statuses (List[SkiRunData]): A list of ski runs current information
            timestamp (float): The time the data was scraped
    """
    
    # turn the ski runs into a dict for json niceness
    write_dict:Dict[str, Dict] = {'timestamp': run_data.timestamp}
    for run_name, run_info in run_data.run_data.items():
        write_dict[run_name] = SkiRunData.get_as_dict_of_strings(run_info)
        del write_dict[run_name]['name']
        
    # open the json file and write the data to it
    with open(f'./data/{run_data.resort}_run_status.json', 'w') as file:
        json.dump(write_dict, file, indent=4)
            
            
def load_resort_run_data_from_file(resort:str) -> SkiRunScrapeData:
    """Load the current run status from a file.
    
    Args:
            resort (str): The name of the resort
    
    Returns:
            run_statuses (SkiRunScrapeData): A list of ski runs current information
    """
    
    with open(f'./data/{resort}_run_status.json', 'r') as file:
        read_dict:Dict[str, Dict] = json.load(file)
        all_run_data:Dict[str, SkiRunData] = {}
        for run_name, run_data in read_dict.items():
            # skip the timestamp
            if run_name == 'timestamp':
                continue
            
            run_data['name'] = run_name
            all_run_data[run_name] = SkiRunData.build_from_dict_of_strings(run_data)
        data = SkiRunScrapeData(read_dict['timestamp'], resort, all_run_data)

    return data
    
    
    