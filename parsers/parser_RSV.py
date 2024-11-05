from includes import *

#---------log in---------
# url_log = 'https://identity.rsv.ru/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Drsv-portal%26redirect_uri%3Dhttps%253A%252F%252Frsv.ru%252Fweb-callback.html%26response_type%3Dcode%26scope%3Dopenid%2520profile%26state%3Daa616a694ce24513951bda51420b0517%26code_challenge%3D0d3JQam6wIR9GoDSppdFRGU-oR-f0iTdvnCC5NLskqc%26code_challenge_method%3DS256%26response_mode%3Dquery'

# service = ChromeService(executable_path=ChromeDriverManager().install())
# options = webdriver.ChromeOptions()
# # options.add_argument("--headless")
# driver = webdriver.Chrome(service=service, options=options)
# driver.get(url_log)
# soup = BeautifulSoup(driver.page_source, "html.parser")

# user_email = 'gauterderfork@gmail.com'
# user_password = 'Forproject404'
# driver.find_element(by ="xpath", value="/html/body/div[2]/div[1]/div/div/div/form/div[1]/div[3]/input").send_keys(user_email)
# sleep(1)
# driver.find_element(by ="xpath", value="/html/body/div[2]/div[1]/div/div/div/form/div[2]/input").send_keys(user_password)
# sleep(30)

url = 'https://rsv.ru/internships/'

service = ChromeService(executable_path=ChromeDriverManager().install())
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
soup = BeautifulSoup(driver.page_source, "html.parser")

#------------------Writing the html code of the page to the file----------------------
# with open('out.html', 'w', encoding='utf-8') as f:
#   f.write(page)

allVacancyCard_link = []
for link in soup.find_all('a', class_='internships-list-items-item'):
  allVacancyCard_link.append('https://rsv.ru' + link.get('href'))

allVacancyCard_link = allVacancyCard_link[:1]

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
  card_data['title'] = str(soupVacancy.find('h1', class_='internship-detail-title').text.replace("\n", ""))
  card_data['short_description'] = str(soupVacancy.find('div', class_='content-wrapper').text.replace("\n", ""))
  card_data['description'] = str(''.join([s.text.replace("\n", "") for s in soupVacancy.find_all('div', class_='content-wrapper')]))

  card_tags = soupVacancy.find('a', class_='badge-industry-name').text.split(', ')
  for tag in soupVacancy.find_all('div', class_='info-blocks-item__text'):
    card_tags.append(tag.text.replace("\n", ""))
  card_data['tags'] = card_tags
  
  sleep(1)
  form_link = soupVacancy.find('a', class_='button size-normal button-red').get('href')

  driver.get(form_link)
  pageForm = driver.page_source
  soupForm = BeautifulSoup(pageForm, "html.parser")
  sleep(5)

  allVacancyForms.append(form_link)

  form_data = {}

  form_data['link'] = form_link
  for thing in soupForm.find_all('label', class_='input__label input__label--holded'):
    name = thing.text
    form_data[name] = {'value': '', 'type':'string'}

  p = 0
  name = ['Статус', 'Статус поиска работы']
  for thing in soupForm.find_all('div', class_='select__options-wrapper'):
    values = []
    for thing2 in thing.find_all('div', class_='select__option-item'):
      values.append(thing2.text)
    form_data[name[p]] = {'value': values, 'type':'select-wrap'}
    p+=1

  thing = soupForm.find('div', class_='select-multi-autocomplete__option-wrapper')
  values = []
  for thing2 in thing.find_all('span', class_='checkbox__text'):
    values.append(thing2.text)
  form_data['Профессиональные навыки'] = {'value': values, 'type':'checkbox-select-wrap'}

  card_data['form'] = form_data
  allVacancyCard_JSON.append(card_data)
    

#-------------------Writing the html code of the forms for vacancies to the file--------------
# with open('allVacancy_form.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyForms:
#     f.write(str(s) + '\n')

with open('Offer/JSON_webs/allVacancyCard_JSON_RSV.json', 'w', encoding='utf-8') as json_file:
  json_file.write("{")
  for for_json in allVacancyCard_JSON:
    json.dump(for_json, json_file, ensure_ascii=False, indent=4)
    json_file.write(",\n")
  json_file.write("{ }\n}")

driver.close()  