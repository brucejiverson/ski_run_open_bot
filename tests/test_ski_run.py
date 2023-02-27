from ski_run_open_bot.ski_run import *


def test_saving_and_loading():
    raw_data:Dict = {
        "timestamp": 8199.620667128,
        "Dean's Dash": {
            "difficulty": 1,
            "status": "Open",
            "mountain_section": "Moonbeam Area"
        },
        "Easy Street": {
            "difficulty": 1,
            "status": "Open",
            "mountain_section": "Moonbeam Area"
        },
        "Home Run": {
            "difficulty": 2,
            "status": "Open",
            "mountain_section": "Moonbeam Area"
        }
    }
    
    run_info = {}
    for key, value in raw_data.items():
        if key == 'timestamp':
            continue
        value['name'] = key
        run_info[key] = SkiRunData.build_from_dict_of_strings(value)
        
    data = SkiRunScrapeData(
        raw_data['timestamp'],
        'solitude',
        run_info
    )    
    
    save_resort_run_status_to_file(data)
    loaded_data = load_resort_run_data_from_file('solitude')
    
    # validate that loaded_data is the same as data
    assert data.timestamp == loaded_data.timestamp
    for run_name in data.run_data.keys():
        run = data.run_data[run_name]
        loaded_run = loaded_data.run_data[run_name]
        
        print(F'Run: {run}')
        print(F'Loaded run: {loaded_run}')
        
        assert run.name == loaded_run.name
        assert run.difficulty == loaded_run.difficulty
        assert run.status == loaded_run.status
        assert run.mountain_section == loaded_run.mountain_section
    

