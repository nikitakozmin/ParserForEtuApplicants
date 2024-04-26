'''This script calculates the current LETI passing scores'''

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import time


def initialize_browser(deployed):
    print('Загрузка браузера...')
    if deployed:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    return webdriver.Chrome(options, service=Service(ChromeDriverManager().install()))


def passing_pages_leti_applicants(handler):
    '''Явная имитация действий пользователя (проще, но дольше, чем парсинг html)'''
    def wrapper(browser):
        elements = browser.find_elements(By.LINK_TEXT, 'перечень')
        count = len(elements)
        print('Обработано страниц:')
        print(f'0/{count}')
        for i in range(count):
            e = browser.find_elements(By.LINK_TEXT, 'перечень')[i]
            browser.execute_script('window.scrollTo(0, {})'.format(e.location['y']))
            time.sleep(1)  # Ожидание прокрутки (желательно переделать)
            e.click()
            handler(browser)
            print(f'{i + 1}/{count}')
            browser.back()
        browser.quit()
    return wrapper


@passing_pages_leti_applicants
def _process_the_pages_leti_applicants(browser):

    # Проверка на бюджет
    e = browser.find_element(By.CLASS_NAME, 'justify-content-between')
    if 'Бюджет' not in e.text:
        return None

    # Нажатие на кнопку "Приоритет №1"
    e = browser.find_element(By.ID, 'priority')
    browser.execute_script('window.scrollTo(0, {})'.format(e.location['y']))
    time.sleep(1)  # Ожидание прокрутки (желательно переделать)
    e.click()

    # Обновление directions и applicants
    e = browser.find_element(By.CLASS_NAME, 'container-content')
    s = e.text
    a = s.splitlines()
    direction = a[1]
    budget = int(a[2].split()[2])
    global directions
    directions[direction] = [None for _ in range(budget)]
    global applicants
    for line in a[12:len(a)]:
        line = line.split()
        line[1] = f'{line[1]} {line[2]}'
        del line[2], line[0]
        line = tuple(line)
        value = applicants.get(line[0], [])
        value.append([
            int(line[1]), direction, line[2], *map(int, line[3:9]), line[9], line[10]
        ])
        applicants[line[0]] = value


def _use_applicants_for_distribution_in_directions():
    print('Компиляция данных...')
    global applicants
    global directions
    while applicants:
        beginners = {k: [tuple(e for e in a) for a in applicants[k]] for k in applicants.keys()}
        applicants.clear()
        for snils, choices in beginners.items():
            choices.sort(key=lambda a: a[0])
            is_passes = False
            for i, choice in enumerate(choices):
                places = directions[choice[1]]
                for j in range(len(places)):
                    if not places[j] and choice[10] == 'Да':
                        places[j] = (snils, choices[i:len(choices)])
                        is_passes = True
                        break
                    #elif choice[2] in ['ОП', 'БВИ', 'ЦК', 'ОК-1', 'ОК-2'] and places[j][1][0][2] == 'ОМ':
                    #    applicants[places[j][0]] = places[j][1]
                    #    places[j] = (snils, choices[i:len(choices)])
                    #    is_passes = True
                    #    break
                    # Желательно заменить сравнения чисел на функцию
                    elif places[j] and choice[10] == 'Да':
                        if choice[3] > places[j][1][0][3]:
                            applicants[places[j][0]] = places[j][1]
                            places[j] = (snils, choices[i:len(choices)])
                            is_passes = True
                            break
                        elif choice[3] < places[j][1][0][3]:
                            continue
                        else:
                            if choice[5] > places[j][1][0][5]:
                                applicants[places[j][0]] = places[j][1]
                                places[j] = (snils, choices[i:len(choices)])
                                is_passes = True
                                break
                            elif choice[5] < places[j][1][0][5]:
                                continue
                            else:
                                if choice[6] > places[j][1][0][6]:
                                    applicants[places[j][0]] = places[j][1]
                                    places[j] = (snils, choices[i:len(choices)])
                                    is_passes = True
                                    break
                                elif choice[6] < places[j][1][0][6]:
                                    continue
                                else:
                                    if choice[7] > places[j][1][0][7]:
                                        applicants[places[j][0]] = places[j][1]
                                        places[j] = (snils, choices[i:len(choices)])
                                        is_passes = True
                                        break
                                    elif choice[7] < places[j][1][0][7]:
                                        continue
                                    else:
                                        if choice[8] > places[j][1][0][8]:
                                            applicants[places[j][0]] = places[j][1]
                                            places[j] = (snils, choices[i:len(choices)])
                                            is_passes = True
                                            break
                                        elif choice[8] < places[j][1][0][8]:
                                            continue
                                        else:
                                            if choice[9] == 'Да' and places[j][1][0][9] == 'Нет':
                                                applicants[places[j][0]] = places[j][1]
                                                places[j] = (snils, choices[i:len(choices)])
                                                is_passes = True
                                                break
                if is_passes:
                    break


def save_min_conditions(directions):
    print('Сохранение данных...')
    name_f = 'Compretition list results.txt'
    with open(name_f, 'w') as f:
        print('Направление: (Минимальное условие зачисления, соответствующий минимальный балл)*', file=f)
        print('*При условии, что все принесут оригинал', file=f)
        print('-' * 40, file=f)
        for direction, applicants in directions.items():
            if applicants:
                print(f'{direction}: {applicants[-1][1][0][2:4]}', file=f)
            else:
                print(f'{direction}: -', file=f)
    print(f'Готово! Результаты загружены в файл "{name_f}"')


if __name__ == '__main__':
    driver = initialize_browser(deployed=True)
    url = 'https://abit.etu.ru/ru/postupayushhim/bakalavriat-i-specialitet/spiski-podavshih-zayavlenie/?competitions=1-1'
    #url = 'file:///C:/Users/kozmi/%D0%9C%D0%BE%D0%B9%20%D0%B4%D0%B8%D1%81%D0%BA/%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D0%B0/%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/Python/Scripts/Python%20files/LocalParserForLetiApplicants/%D0%A1%D0%BF%D0%B8%D1%81%D0%BA%D0%B8%20%D0%BF%D0%BE%D0%B4%D0%B0%D0%B2%D1%88%D0%B8%D1%85%20%D0%B7%D0%B0%D1%8F%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5.html'
    driver.get(url)
    directions, applicants = dict(), dict()
    _process_the_pages_leti_applicants(driver)
    _use_applicants_for_distribution_in_directions()
    save_min_conditions(directions)
    time.sleep(3)
