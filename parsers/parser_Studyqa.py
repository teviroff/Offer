from includes import *

url = 'https://ru.studyqa.com/internships/countries/cities/industries?page='

service = ChromeService(executable_path=ChromeDriverManager().install())

options = webdriver.ChromeOptions()
# options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)

#------------------Writing the html code of the page to the file----------------------
# with open('out.html', 'w', encoding='utf-8') as f:
#   f.write(page)

culc = 0
allVacancyCard_link = []
for page in range(1, 8):
  driver.get(url + f'{page}')
  page = driver.page_source

  soup = BeautifulSoup(page, "html.parser")
  allVacancyCard = soup.findAll('div', class_='cards__list')
  for link in soup.findAll('a', class_='btn btn-secondary'):
    culc+=1
    print(culc)
    allVacancyCard_link.append(link.get('href'))

# allVacancyCard_link = allVacancyCard_link[:1]

#------------------Writing the html code of the job cards to the file----------------
# with open('allVacancy.html', 'w', encoding='utf-8') as f:
#   f.write(str(allVacancyCard))

#------------------Writing links to vacancies in the file--------------------------------
# with open('allVacancy_link.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyCard_link:
#     f.write(str(s) + '\n')

allVacancyForms = []
allVacancyCard_JSON = []
for link in allVacancyCard_link:
  card_data = {}

  driver.get(link)
  pageVacancy = driver.page_source
  soupVacancy = BeautifulSoup(pageVacancy, "html.parser")

  card_data['link'] = link
  card_data['title'] = str(soupVacancy.find('div', class_='page__title seo__item').text.replace("\n", ""))
  card_data['short_description'] = str(soupVacancy.find('div', class_='text__custom').text.replace("\n", ""))
  card_data['description'] = str(soupVacancy.find('div', class_='section sc__main sc__main-country').text.replace("\n", ""))

  card_tags=[]
  tags = soupVacancy.find('div', class_='page__descr')
  for tag in tags.find_all('li'):
    card_tags.append(tag.text.replace("\n", ""))
  card_data['tags'] = card_tags
  
  sleep(1)
  form_link = link + soupVacancy.find('a', class_='btn btn-primary d-flex align-items-center toggle__form-js').get('href')


  allVacancyForms.append(form_link)

  form_data = {}

  form_data['link'] = form_link

  soupForm = soup.find('div', class_='form-group')
  for thing in soupForm.findAll('div', class_='form-field'):
    if(thing.find('div', class_='select-wrap') is None):
      name = thing.find('input').get('placeholder')
      form_data[name] = {'value': '', 'type':'string'}
      
  for thing in soupForm.findAll('div', class_='select-wrap'):
    name = thing.get('data-placeholder')
    values = []
    for thing2 in thing.findAll('option'):
      if(thing2.get('value') is not None):
        values.append((thing2.get('value'), thing2.text))
    form_data[name] = {'value': values, 'type':'select-wrap'}

  card_data['form'] = form_data
  allVacancyCard_JSON.append(card_data)
    

#-------------------Writing the html code of the forms for vacancies to the file--------------
# with open('allVacancy_form.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyForms:
#     f.write(str(s) + '\n')

with open('Offer/JSON_webs/allVacancyCard_JSON_Studyqa.json', 'w', encoding='utf-8') as json_file:
  json_file.write("{")
  for for_json in allVacancyCard_JSON:
    json.dump(for_json, json_file, ensure_ascii=False, indent=4)
    json_file.write(",\n")
  json_file.write("{ }\n}")

driver.close()  