from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from time import time


# First of, we need to download ChromeDriver from the internet in order to work with Chrome (since I work with it) in
# Selenium. Then we need to specify a path the downloaded chromedriver file is at

def download_stock_data(ticker, delay):
    """
    This function firstly goes to Yahoo website with specific tickers that mentioned in the assignment. Then it clicks
    at 'Historical Data' tab, then unfolds a drop down menu for Time Period button, clicks at MAX button and downloads
    all the ticker's daily stock prices.
    """

    driver = webdriver.Chrome(CHROMEDRIVER)
    driver.get(f'{BASE_URL}/quote/{ticker}')

    # That is why we wrap up following code into try-except block to catch an error or a bag and quit the browser
    # otherwise
    try:
        hist_data = WebDriverWait(driver, timeout=delay).until(
            ec.presence_of_element_located((By.LINK_TEXT, 'Historical Data'))
        )
        hist_data.click()

        time_period_button_css_selector = '#Col1-1-HistoricalDataTable-Proxy > section > ' \
                                          'div.Pt\(15px\).drop-down-selector.historical > ' \
                                          'div.Bgc\(\$lv1BgColor\).Bdrs\(3px\).P\(10px\) > div:nth-child(1) > div > ' \
                                          'div > div'

        time_period = WebDriverWait(driver, timeout=delay).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, time_period_button_css_selector))
        )
        time_period.click()

        max_button_css_selector = '#dropdown-menu > div > ul:nth-child(2) > li:nth-child(4) > button'
        max_button = WebDriverWait(driver, timeout=delay).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, max_button_css_selector))
        )
        max_button.click()

        download_css_selector = '#Col1-1-HistoricalDataTable-Proxy > section > div.Pt\(15px\).drop-down-selector' \
                                '.historical > div.C\(\$tertiaryColor\).Mt\(20px\).Mb\(15px\) > span.Fl\(end\)' \
                                '.Pos\(r\).T\(-6px\) > a'
        download = WebDriverWait(driver, timeout=delay).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, download_css_selector))
        )
        download.click()
    except:
        driver.quit()


def update_file(stock_name_file, path):
    """
    This function reads file from Yahoo downloaded (Downloads folder on my computer) and adds one column that is a ratio
    of current close price to close price 3 session days prior. It writes into a csv file with ticker's name with dates
    in descending order as it has been mentioned in the assignment. However, firstly, we need to check if a file
    actually exists
    """

    if os.path.exists(f'/Users/macbookpro/Downloads/{stock_name_file}.csv'):
        data = pd.read_csv(f'/Users/macbookpro/Downloads/{stock_name_file}.csv')

        # Creates a new column and writes required parameters into it. 
        data['3day_before_change'] = round(data['Close'] / data['Close'].shift(3), 4)

        # I noticed the assignment had dates listed in descending order. That is exactly what this line does.
        data = data.sort_values(by='Date', ascending=False)

        # Changes indices order. I could have just skip this line of code because I do not include indices in a csv file
        indices = data.index.sort_values(ascending=True)
        data = data.set_index(indices)
        data.to_csv(f'{path}/{stock_name_file}.csv', index=False)


def download_company_news(stock_name_file, b_url, path):
    """
    This function uses BeautifulSoup and Pandas to extract the data
    """

    req = requests.get(f'{b_url}/quote/{stock_name_file}')
    soup = BeautifulSoup(req.text, 'html.parser')
    news = soup.select('h3.Mb(5px) a')


    if news:
        article_links = []
        article_headers = []
        for n in news:
            url = b_url + n.get("href")
            req = requests.get(url)
            soup_news = BeautifulSoup(req.text, 'html.parser')
            article_links.append(url)
            article_headers.append(soup_news.select('h1')[0].text)
        df = pd.DataFrame()
        df['link'] = article_links
        df['title'] = article_headers
        df.to_csv(f'{path}/{stock_name_file}_news.csv', index=False)


if __name__ == '__main__':

    start = time()

    CHROMEDRIVER = '/Users/macbookpro/Desktop/Desktop/ChromeDriver/chromedriver'
    BASE_URL = 'https://finance.yahoo.com'

    # This is my local path I am going to use. In your case you can use any path you want
    DOWNLOAD_PATH = '/Users/macbookpro/Desktop/Desktop/PyCharm/Python_projects/Test_assignments/IntroLab Systems'

    # We need this constant in order to secure a next operation that is going to happen in case a previous web page has
    # not still loaded
    DELAY = 5

    tickers = [
        'PD',
        'ZUO',
        'PINS',
        'ZM',
        'DOCU',
        'CLDR',
        'RUN',
        'PVTL']

    for tckr in tickers:
        # This function in the loop solves the problems 1-4 from the assignment
        download_stock_data(tckr, DELAY)

    for tckr in tickers:
        # The function corresponds to the problems 5-6
        update_file(tckr, DOWNLOAD_PATH)
        print(tckr)

    for tckr in tickers:
        # That solves the problem 7
        download_company_news(tckr, BASE_URL, DOWNLOAD_PATH)
        print(tckr)

    print('It took ', time() - start)

