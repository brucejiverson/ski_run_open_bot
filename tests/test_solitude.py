from ski_run_open_bot.solitude_utah import *


def validate_ski_run_data():
    # load the data
    data = scrape_ski_run_information()
    assert data.run_data is not None 
    assert len(data.run_data) > 0

