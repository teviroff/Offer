from includes import *

url = 'https://www.ciee.org/in-the-usa/research-training/intern-professional-training/internships?page='
json_file = open('Offer/JSON_webs/allVacancyCard_JSON_CIEE.json', 'a', encoding='utf-8')

service = ChromeService(executable_path=ChromeDriverManager().install())

options = webdriver.ChromeOptions()
options.timeouts = { 'pageLoad': 5000 }
# options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)

#------------------Writing the html code of the page to the file----------------------
# with open('out.html', 'w', encoding='utf-8') as f:
#   f.write(page)

culc = 0
allVacancyForms = []
allVacancyCard_JSON = []
json_file.write("{")
for page in range(1, 5):
  try:
    driver.get(url + f'{page}') 
  except:
    continue
  page = driver.page_source
  soup = BeautifulSoup(page, "html.parser")
  for soupVacancy in soup.find_all('article', class_='internship internship--inbound internship--modal'):
    card_data = {}

    card_data['id'] = culc
    card_data['link'] = url
    card_data['title'] = str(soupVacancy.find('div', class_='internship--modal__header-wrapper').find('h2').text.replace("\n", ""))
    card_data['description'] = str(''.join([txt.text for txt in soupVacancy.find_all('div', class_='global-spacing--large-alt')])).replace("\n", "")
    card_data['short_description'] = card_data['description']

    card_data['tags']  = str(soupVacancy.find('div', class_='internship--modal__main-info global-spacing--large-alt').text.replace("\n", ""))

    form_data = {
      'First Name'  : {'value': '', 'type':'string'},
      'Last Name' : {'value': '', 'type':'string'},
      'Email' : {'value': '', 'type':'string'},
      'Phone' : {'value': '', 'type':'string'},
      'Are you a current college student or recent graduate?' : {'value': '', 'type':'string'},
      'College/University Name' : {'value': '', 'type':'string'},
      'College/University Graduation Year' : {'value': '', 'type':'string'},
      'Industry of Interest' : {'value': '', 'type':'string'},
      'Desired Program Start Month' : {'value': '', 'type':'string'},
      'Desired Program Start Year' : {'value': '', 'type':'string'},
      'Country of Residence' : {'value': '', 'type':'string'},
      }

    card_data['form'] = form_data
    allVacancyCard_JSON.append(card_data)

    json.dump(card_data, json_file, ensure_ascii=False, indent=4)
    json_file.write(",\n")

    culc+=1
    print(culc)
    card_data['id'] = culc

json_file.write("{ }\n}")
    

#-------------------Writing the html code of the forms for vacancies to the file--------------
# with open('allVacancy_form.html', 'w', encoding='utf-8') as f:
#   for s in allVacancyForms:
#     f.write(str(s) + '\n')

driver.close()  