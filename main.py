from pprint import pprint
from time import sleep
import requests
from bs4 import BeautifulSoup
import json
import fake_useragent


def get_search_link(key_words: list,
                    regions: list):  # key_words = ['python', 'django', 'flask'] regions = 1: Москва, 2: Санкт-Петербург
    area_text = ''
    for city in regions:
        area_text += f'&area={city}'
    link = f'https://spb.hh.ru/search/vacancy?text={"+".join(key_words)}{area_text}' # link = 'https://spb.hh.ru/search/vacancy?text=python+django+flask&area=1&area=2'
    return link

job_search_parsed = []

def get_job_search_dict():
    link = get_search_link(['python', 'django', 'flask'], [1, 2])

    user = fake_useragent.UserAgent().random

    headers = {'User-Agent': user}  # https://browser-info.ru/

    for page in range(0, 3):
        job_search_link = link + f"&page={page}"
        print(f'page #{page}, link = {job_search_link}')
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

            response = requests.get(job_link, headers=headers)
            job_info = response.text
            job_info_soup = BeautifulSoup(job_info, "lxml")

            salary_range_list = job_info_soup.find("div", class_="vacancy-title").find_all('span')

            if len(salary_range_list) == 0:
                salary_range = 'з/п не указана'
            else:
                salary_range = job_info_soup.find("div", class_="vacancy-title").find_all('span')[0].text.strip().replace('\xa0', ' ')

            city_name_tag = job_info_soup.find("div", class_='vacancy-company-redesigned').find('p')

            if bool(city_name_tag) == True:
                city_name_tag_list = job_info_soup.find("div", class_='vacancy-company-redesigned').find('p')
                city_name = city_name_tag_list.text.split()[0]
            else:
                city_name_tag_list = job_info_soup.find("div", class_='vacancy-company-redesigned').find_all('a')[
                    -1].find('span')
                city_name = city_name_tag_list.text.split()[0]

            vacancy_dict = {
                'job title': job_title,
                "job description": job_link,
                "salary range": salary_range,
                "company name": company_name,
                "city name": city_name,
                'company profile': company_link
            }
       #     print(vacancy_dict)
            job_search_parsed.append(vacancy_dict)
    print(f'Данные готовы для заливки в файл. Всего собрано {len(job_search_parsed)} вакансий.')
    return job_search_parsed

def get_json():
    with open('job_search_parsed.json', 'w', encoding='utf-8') as file:
        json_data = file.write(json.dumps(job_search_parsed, indent=4, ensure_ascii=False))
        print('Данные загружены в файл job_search_parsed.json')
        return json_data

def get_json2print():
    with open('job_search_parsed.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        pprint(data)
        print(json.dumps(data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': ')))
        return

if __name__ == '__main__':
    get_job_search_dict()
    get_json()
    get_json2print()
