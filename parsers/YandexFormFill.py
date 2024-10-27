from includes import *

from parser_Yandex import allFormsJSON

for card in allFormsJSON:
  link = card['link']
  service = ChromeService(executable_path=ChromeDriverManager().install())
  options = webdriver.ChromeOptions()
  # options.add_argument("--headless")
  driver = webdriver.Chrome(service=service, options=options)
  driver.get(link)
  soupForm = BeautifulSoup(driver.page_source, "html.parser")
  sleep(1)

  values = []
  for atribute in card:
    if atribute != 'link' and atribute != 'Добавить резюме':
      values.append(card[atribute]['value'])
  pos = 0

  dom = etree.HTML(str(soupForm))
  tree = etree.ElementTree(dom)
  formInputs = dom.xpath('//*/span/span/input')
  for thing in formInputs:
    driver.find_element(by ="xpath", value=tree.getpath(thing)).send_keys(values[pos])
    pos += 1
    sleep(2)
  formInputs = dom.xpath('//*/textarea')
  for thing in formInputs:
    driver.find_element(by ="xpath", value=tree.getpath(thing)).send_keys(values[pos])
    pos += 1
    sleep(2)

  driver.find_element(by ="xpath", value="/html/body/div[1]/div/main/form/div/div[10]/div/div/div[1]/label/span[1]/input").click()
  driver.find_element(by ="xpath", value="/html/body/div[1]/div/main/form/div/div[11]/div/div/div[1]/label/span[1]/input").click()
  driver.find_element(by ="xpath", value="/html/body/div[1]/div/main/form/div/div[12]/div/div/div[1]/label/span[1]/input").click()
  sleep(30)
