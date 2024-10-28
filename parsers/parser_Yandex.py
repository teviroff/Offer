from includes import *

url = 'https://yandex.ru/jobs/vacancies?text=стажёр'

service = ChromeService(executable_path=ChromeDriverManager().install())

options = webdriver.ChromeOptions()
# options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
page = driver.page_source

soup = BeautifulSoup(page, "html.parser")

#------------------Writing the html code of the page to the file----------------------
# with open('out.html', 'w', encoding='utf-8') as f:
#   f.write(page)

allVacancyCard_link = []
allVacancyCard = soup.findAll('span', class_='lc-jobs-vacancy-card')
for link in soup.findAll('a', class_='lc-jobs-vacancy-card__link'):
  allVacancyCard_link.append('https://yandex.ru' + link.get('href'))
allVacancyCard_link = allVacancyCard_link[1:]

allVacancyCard_link = allVacancyCard_link[:1]

#------------------Writing the html code of the job cards to the file----------------
# with open('allVacancy.html', 'w', encoding='utf-8') as f:
#   f.write(str(allVacancyCard))

#------------------Writing links to vacancies in the file--------------------------------
# with open('allVacancy_link.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyCard_link:
#     f.write(str(s) + '\n')

allVacancyForms = []
allFormsJSON = []
allVacancyCard_JSON = []
for link in allVacancyCard_link:
  card_data = {}

  driver.get(link)
  pageVacancy = driver.page_source
  soupVacancy = BeautifulSoup(pageVacancy, "html.parser")

  card_data['link'] = link
  card_data['title'] = (soupVacancy.find('h1', class_='lc-styled-text__text').text if soupVacancy.find('h1', class_='lc-styled-text__text') is not None else '')
  card_data['short_description'] = (soupVacancy.find('section', class_='lc-jobs-common-section').text if soupVacancy.find('section', class_='lc-jobs-common-section') is not None else '')
  card_data['description'] = (soupVacancy.find('div', class_='lc-jobs-vacancy-mvp__description').text if soupVacancy.find('div', class_='lc-jobs-vacancy-mvp__description') is not None else '')

  card_tags=[]
  for tag in soupVacancy.find_all('span', class_='Text Text_typography_control-s lc-jobs-tag__label'):
    card_tags.append(tag.text)
  card_data['tags'] = card_tags
  
  sleep(1)
  tmp1 = soupVacancy.find('iframe', class_='lc-iframe__iframe')
  while(tmp1 is None):
    driver.get(link)
    pageVacancy = driver.page_source
    soupVacancy = BeautifulSoup(pageVacancy, "html.parser")
    sleep(1)
    tmp1 = soupVacancy.find('iframe', class_='lc-iframe__iframe')
  
  tmp = tmp1.get('src')
  form_link = ''
  for s in tmp:
    if s != '?':
      form_link += s
    else:
      break

  allVacancyForms.append(form_link)
  driver.get(form_link)
  sleep(1)
  pageForm = driver.page_source
  soupForm = BeautifulSoup(pageForm, "html.parser")

  form_data = {}

  form_data['link'] = form_link

  for thing in soupForm.findAll('div', class_='QuestionMarkup TextQuestion Question'):
    for thing2 in thing.findAll('ol'):
      form_data[thing2.text.replace("\n", "")] = {'value': '1', 'type':'string'}
    for thing2 in thing.findAll('p'):
      if thing2.text != '&nbsp;':
        form_data[thing2.text.replace("\n", "")] = {'value': '2', 'type':'string'}
      
  for thing in soupForm.findAll('div', class_='QuestionMarkup FileQuestion Question'):
    for thing2 in thing.findAll('ol'):
      form_data[thing2.text.replace("\n", "")] = {'value': '3', 'type':'file'}
    for thing2 in thing.findAll('p'):
      if thing2.text != '&nbsp;' and thing2.text != 'Выберите файл':
        form_data[thing2.text.replace("\n", "")] = {'value': '4', 'type':'file'}

  allFormsJSON.append(form_data)
  card_data['form'] = form_data
  allVacancyCard_JSON.append(card_data)
    

#-------------------Writing the html code of the forms for vacancies to the file--------------
# with open('allVacancy_form.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyForms:
#     f.write(str(s) + '\n')

# with open('allVacancy_formData.json', 'w', encoding='utf-8') as json_file:
#   json_file.write("{")
#   for for_json in allFormsJSON:
#     json.dump(for_json, json_file, ensure_ascii=False, indent=4)
#     json_file.write(",\n")
#   json_file.write("{ }\n}")

with open('Offer/JSON_webs/allVacancyCard_JSON.json', 'w', encoding='utf-8') as json_file:
  json_file.write("{")
  for for_json in allVacancyCard_JSON:
    json.dump(for_json, json_file, ensure_ascii=False, indent=4)
    json_file.write(",\n")
  json_file.write("{ }\n}")

driver.close()  