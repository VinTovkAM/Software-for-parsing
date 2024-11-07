from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from time import sleep


def create_df(sport, params):
    custom_options = Options()
    custom_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=custom_options) 
    link = 'https://www.flashscorekz.com/'
    driver.get(link)
    
    sports_dict = {
        'ИЗБРАННОЕ': 0,
        'ФУТБОЛ': 1,
        'ХОККЕЙ': 2,
        'ТЕННИС': 3,
        'БАСКЕТБОЛ': 4,
        'ВОЛЕЙБОЛ': 5,
        'ГАНДБОЛ': 6
    }

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'menuTop__text')))
    driver.find_elements(By.CLASS_NAME, 'menuTop__text')[sports_dict[sport]].click()

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'event__match')))
    
    elements = driver.find_elements(By.CLASS_NAME, 'event__match.event__match--withRowLink.event__match--scheduled.event__match--twoLine')

    ids = []
    final = []
    
    for element in elements:
        element_id = element.get_attribute("id")
        ids.append(element_id[4:])

    for match_id in ids:
        statistic = f'https://www.flashscorekz.com/match/{match_id}/#/match-summary/match-summary/match-statistics/0'
        driver.get(statistic)
        sleep(5)

        league = driver.find_elements(By.CLASS_NAME, 'tournamentHeader__country')[0].text
        team_1 = driver.find_elements(By.CLASS_NAME, 'duelParticipant__home')[0].text
        team_2 = driver.find_elements(By.CLASS_NAME, 'duelParticipant__away')[0].text
        date = driver.find_elements(By.CLASS_NAME, 'duelParticipant__startTime')[0].text
        status = driver.find_elements(By.CLASS_NAME, 'detailScore__status')[0].text
        score = driver.find_elements(By.CLASS_NAME, 'detailScore__wrapper')[0].text.splitlines()[::2]

        statistics_elements = driver.find_elements(By.CLASS_NAME, '_row_rz3ch_9')
        
        statistics_dict = {}
        
        for element in statistics_elements:
            static = element.text.splitlines()
            if len(static) < 3:
                continue
            key = static[1]
            value_host = static[0]
            value_guest = static[-1]
            if key in params:
                statistics_dict[key] = [value_host, value_guest]
    
        for param in params:
            if param not in statistics_dict:
                statistics_dict[param] = ['-', '-']
    
        match_info_df = pd.DataFrame([[league, date, status, team_1, team_2, score[0], score[-1]]],
                                     columns=['Лига', 'Дата', 'Статус', 'Хозяева', 'Гости', 'Счет хозяев', 'Счет гостей'])
        
        df = pd.DataFrame(statistics_dict)

        home_info = df.loc[[0]]
        home_info = home_info.add_suffix('_home')
        away_info = df.loc[[1]]
        away_info = away_info.add_suffix('_away')
        away_info = away_info.reset_index(drop=True)
    
        final_dop_info = pd.merge(home_info, away_info, left_index=True, right_index=True)
        final_stat = pd.merge(match_info_df, final_dop_info, left_index=True, right_index=True)
    
        final.append(final_stat)

    driver.quit()

    return final


def main():
    sport = 'ХОККЕЙ'
    params = ['Броски в створ ворот', 'Удаления']
    final = create_df(sport, params)
    final_df = pd.concat(final, ignore_index=True)
    final_df.to_excel("output_data.xlsx", index=False)


if __name__ == '__main__':
    main()