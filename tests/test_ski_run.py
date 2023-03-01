from ski_run_open_bot.ski_run import *


raw_data = {
    "timestamp": 8199.620667128,
    "resort": "solitude",
    "run_data": {
        "Dean's Dash": {
            "difficulty": 1,
            "status": "Open",
            "mountain_section": "Moonbeam Area"
        },
        "Easy Street": {
            "difficulty": 3,
            "status": "Open",
            "mountain_section": "Moonbeam Area"
        },
        "Home Run": {
            "difficulty": 3,
            "status": "Open",
            "mountain_section": "Moonbeam Area"
        },
        
        "Dummy Run": {
            "difficulty": 3,
            "status": "Closed",
            "mountain_section": "Moonbeam Area"
        },
    }
}


def test_saving_and_loading():
    global raw_data
    
    data = SkiRunScrapeData.build_from_raw_dict(raw_data)
    
    save_resort_run_status_to_file(data, file_name_override='_test.json')
    loaded_data = load_resort_run_data_from_file('solitude', file_name_override='_test.json')
    
    # validate that loaded_data is the same as data
    assert data.timestamp == loaded_data.timestamp
    for run_name in data.run_data.keys():
        run = data.run_data[run_name]
        loaded_run = loaded_data.run_data[run_name]
        
        print(F'Run: {run}')
        print(F'Loaded run: {loaded_run}')
        
        assert run.difficulty == loaded_run.difficulty
        assert run.status == loaded_run.status
        assert run.mountain_section == loaded_run.mountain_section
    

def test_detecting_opened_runs():
    initial_data = SkiRunScrapeData.build_from_raw_dict(raw_data)
    altered_data = SkiRunScrapeData.build_from_raw_dict(raw_data)
    altered_data.run_data["Dean's Dash"].status= RunStatus.OPEN
    altered_data.run_data["Dummy Run"].status= RunStatus.OPEN
    altered_data.run_data["Easy Street"].status= RunStatus.OPEN
    
    opened = filter_for_opened_runs(altered_data.run_data, initial_data.run_data)
    
    assert len(opened.keys()) == 1
    assert list(opened.keys())[0] == "Dummy Run"
    
 
if __name__ == "__main__":
     test_detecting_opened_runs()
     