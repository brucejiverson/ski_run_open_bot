from ski_run_open_bot.solitude_utah import *


def test_scraping_ski_run_data():
    """Warning: this will webscrape the actual website."""
    # load the data
    data = scrape_ski_run_information()
    assert data.run_data is not None 
    assert len(data.run_data) > 0


if __name__ == '__main__':
    test_scraping_ski_run_data()