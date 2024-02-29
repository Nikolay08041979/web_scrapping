from pprint import pprint
from time import sleep
import requests
from bs4 import BeautifulSoup
import json


def get_search_link(key_words: list,
                    regions: list):  # key_words = ['python', 'django', 'flask'] regions = 1: Москва, 2: Санкт-Петербург
    area_text = ''
    for city in regions:
        area_text += f'&area={city}'
    link = f'https://spb.hh.ru/search/vacancy?text={"+".join(key_words)}{area_text}'
    #   link = 'https://spb.hh.ru/search/vacancy?text=python+django+flask&area=1&area=2'
    return link


link = get_search_link(['python', 'django', 'flask'], [1, 2])
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}

job_search_parsed = []

for page in range(0, 3):
    print(page)
    job_search_link = link + f"&page={page}"
    response = requests.get(job_search_link, headers=headers)
    if response.status_code != 200:
        break

    main_html = response.text
    sleep(3)
    main_soup = BeautifulSoup(main_html, "lxml")

    job_script_list_tag = main_soup.find_all("div", class_='vacancy-serp-item__layout')

    for job_script_tag in job_script_list_tag:
        job_title = job_script_tag.find("h3", class_='bloko-header-section-3').text
        job_link = job_script_tag.find("h3", class_='bloko-header-section-3').find("a", class_="bloko-link").get(
            "href")

        company_tag = job_script_tag.find("a", class_="bloko-link bloko-link_kind-tertiary")
        company_name = company_tag.text.replace('\xa0', ' ')
        company_link_relative = company_tag["href"]
        company_link = f"https://spb.hh.ru{company_link_relative}"

        # job_counter = job_script_tag.find("div", class_="vacancies-search-header").find('h1')[0].text.strip()
        #
        # if len(job_search_parsed) == int(job_counter):
        #     break

        response = requests.get(job_link, headers=headers)
        job_info = response.text
        job_info_soup = BeautifulSoup(job_info, "lxml")
        salary_range = job_info_soup.find("div", class_="vacancy-title").findNext('span',
                                                                                  class_='bloko-header-section-2 bloko-header-section-2_lite').text.replace(
            '\xa0', ' ')

        response = requests.get(company_link, headers=headers)
        company_info = response.text
        company_info_soup = BeautifulSoup(company_info, "lxml")

        try:
            city_name = company_info_soup.find("div", class_='employer-sidebar-block').text
        except:
            city_name = '-'

        vacancy_dict = {
            "job description": job_link,
            "salary range": salary_range,
            "company name": company_name,
            "city name": city_name,
            'company profile': company_link
        }

        job_search_parsed.append(vacancy_dict)

print(job_search_parsed)


def get_json():
    with open('job_search_parsed.json', 'w', encoding='utf-8') as file:
        json_data = file.write(json.dumps(job_search_parsed, indent=4, encoding='utf-8', ensure_ascii=False))
    return json_data


print(get_json())


def get_json_update():  # put a param on which need to prove the list
    with open('job_search_parsed.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for i in range(len(data)):
            if data[i]['salary range'] == data[i]['company name']:
                data[i]['salary range'] = '-'
                with open('job_search_parsed.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
        return


# print(get_json_update())

def get_json_print():
    with open('job_search_parsed.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        pprint(data)
        print(json.dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': ')))
        return f'Всего загружено {len(data)} вакансий.'

# print(get_json_print())
