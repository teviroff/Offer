from includes import *

url = 'https://career.habr.com/vacancies?qid=1&type=all&page='
json_file = open('Offer/JSON_webs/allVacancyCard_JSON_Habr.json', 'a', encoding='utf-8')

service = ChromeService(executable_path=ChromeDriverManager().install())

options = webdriver.ChromeOptions()
options.timeouts = { 'pageLoad': 5000 }
# options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)

#------------------Writing the html code of the page to the file----------------------
# with open('out.html', 'w', encoding='utf-8') as f:
#   f.write(page)

allVacancyCard_link = []
for page in range(1, 7):
  try:
    driver.get(url + f'{page}') 
  except:
    continue
  page = driver.page_source
  soup = BeautifulSoup(page, "html.parser")
  for link in soup.find_all('a', class_='vacancy-card__title-link'):
    allVacancyCard_link.append('https://career.habr.com' + link.get('href'))

# allVacancyCard_link = allVacancyCard_link[:1]

#------------------Writing the html code of the job cards to the file----------------
# with open('allVacancy.html', 'w', encoding='utf-8') as f:
#   f.write(str(allVacancyCard))

#------------------Writing links to vacancies in the file--------------------------------
# with open('allVacancy_link.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyCard_link:
#     f.write(str(s) + '\n')

culc = 0
allVacancyForms = []
allVacancyCard_JSON = []
json_file.write("[")
for link in allVacancyCard_link:
  card_data = {}

  try:
    driver.get(link)
  except:
    continue
  pageVacancy = driver.page_source
  soupVacancy = BeautifulSoup(pageVacancy, "html.parser")

  card_data['id'] = culc
  card_data['link'] = link
  card_data['title'] = str(soupVacancy.find('h1', class_='page-title__title').text.replace("\n", ""))
  card_data['short_description'] = str((soupVacancy.find('div', class_='vacancy-description__text').find('p').text if soupVacancy.find('div', class_='vacancy-description__text') is not None else '')).replace("\n", "")
  card_data['description'] = str((soupVacancy.find('div', class_='vacancy-description__text').text if soupVacancy.find('div', class_='vacancy-description__text') is not None else '')).replace("\n", "")

  card_data['tags']  = (''.join([(tag.find('span', class_='inline-list').text if tag.find('span', class_='inline-list') is not None else '') for tag in soupVacancy.find_all('div', class_='content-section')])).replace('\n\n', '\n').replace('\t', '').split('\n')

  form_data = {
    'Email'  : {'value': '', 'type':'string'},
    'Никнейм' : {'value': '', 'type':'string'},
    'Пароль' : {'value': '', 'type':'string'},
    'Имя' : {'value': '', 'type':'string'},
    'Фамилия' : {'value': '', 'type':'string'},
    'Пол' : {'value': '', 'type':'string'},
    'Дата рождения' : {'value': '', 'type':'string'},
    'Специализация' : {'value': '', 'type':'string'},
    'Профессиональные навыки' : {'value': '', 'type':'string'}
    }

  card_data['form'] = form_data
  allVacancyCard_JSON.append(card_data)

  json.dump(card_data, json_file, ensure_ascii=False, indent=4)
  json_file.write(",\n")

  culc+=1
  print(culc)
  card_data['id'] = culc

json_file.write("{ }\n]")

#-------------------Writing the html code of the forms for vacancies to the file--------------
# with open('allVacancy_form.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyForms:
#     f.write(str(s) + '\n')

driver.close()  