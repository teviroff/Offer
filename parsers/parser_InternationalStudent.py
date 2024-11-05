from includes import *

url = 'https://www.internationalstudent.com/school-search/school/search/?page='
json_file = open('Offer/JSON_webs/allVacancyCard_JSON_InternationalStudent.json', 'a', encoding='utf-8')

service = ChromeService(executable_path=ChromeDriverManager().install())

options = webdriver.ChromeOptions()
# options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)

#------------------Writing the html code of the page to the file----------------------
# with open('out.html', 'w', encoding='utf-8') as f:
#   f.write(page)

allVacancyCard_link = []
for num in range(1, 143):
  try:
    driver.get(url + f'{num}')
    page = driver.page_source
  except:
    continue

  soup = BeautifulSoup(page, "html.parser")
  for link in soup.find_all('a', class_='font-bitter text-left text-danger mb-2 mb-lg-0'):
    allVacancyCard_link.append('https://www.internationalstudent.com' + link.get('href'))

driver.close() 
# allVacancyCard_link = allVacancyCard_link[:1]

#------------------Writing the html code of the job cards to the file----------------
# with open('allVacancy.html', 'w', encoding='utf-8') as f:
#   f.write(str(allVacancyCard))

#------------------Writing links to vacancies in the file--------------------------------
# with open('allVacancy_link.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyCard_link:
#     f.write(str(s) + '\n')

options = webdriver.ChromeOptions()
options.timeouts = { 'pageLoad': 5000 }
# options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

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
  card_data['title'] = str(soupVacancy.find('h1').text.replace("\n", ""))
  card_data['short_description'] = str((soupVacancy.find('div', {"id": 'school-info-mission'}).text if soupVacancy.find('div', {"id": 'school-info-mission'}) is not None else '')).replace("\n", "")
  card_data['description'] = str((soupVacancy.find('div', class_='markdown-content').text if soupVacancy.find('div', class_='markdown-content') is not None else '')).replace("\n", "")

  card_data['tags']  = (''.join([tag.text for tag in soupVacancy.find('div', class_='col-sm d-flex flex-column justify-content-between').find_all('div')] if soupVacancy.find('div', class_='col-sm d-flex flex-column justify-content-between') is not None else [])).replace('\n\n', '\n').replace('\t', '').split('\n')
  
  form_link = link

  form_data = {}
  form_data['link'] = form_link

  soupForm = soupVacancy.find('div', class_='card card-body bg-light shadow rounded-0')
  formFilds = soupForm.find('div', class_='row')
  for thing in formFilds.find_all('label', class_='mb-1 col-sm-4 col-md-3 col-lg-4 col-form-label text-md-right'):
    form_data[str(thing.text)] = {'value': '', 'type':'string'}
      
  for thing in soupForm.findAll('div', class_='select-wrap'):
    name = thing.get('data-placeholder')
    values = []
    for thing2 in thing.findAll('option'):
      if(thing2.get('value') is not None):
        values.append((thing2.get('value'), thing2.text))
    form_data[name] = {'value': values, 'type':'select-wrap'}

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