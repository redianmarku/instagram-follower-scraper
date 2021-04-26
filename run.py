import os
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM

# complete these 2 fields ==================
USERNAME = 'your instagram username'
PASSWORD = 'your instagram password'
# ==========================================

usr = input('Put the username for scrapping followers from: ')

user_input = input(
    'Put how many followers you want to scrape (60-500 recommanded):')
TIME = 0.069 * int(user_input)


def scrape(username):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--log-level=3")

    mobile_emulation = {
        "userAgent": 'Mozilla/5.0 (Linux; Android 4.0.3; HTC One X Build/IML74K) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/83.0.1025.133 Mobile Safari/535.19'
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(executable_path=CM().install(), options=options)

    bot.get('https://instagram.com/')
    bot.set_window_size(500, 950)
    time.sleep(5)
    bot.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/article/div/div/div/div[3]/button[1]').click()
    print("Logging in...")
    time.sleep(1)
    username_field = bot.find_element_by_xpath(
        '/html/body/div[1]/section/main/article/div/div/div/form/div[1]/div[3]/div/label/input')
    username_field.send_keys(USERNAME)

    find_pass_field = (
        By.XPATH, '/html/body/div[1]/section/main/article/div/div/div/form/div[1]/div[4]/div/label/input')
    WebDriverWait(bot, 50).until(
        EC.presence_of_element_located(find_pass_field))
    pass_field = bot.find_element(*find_pass_field)
    WebDriverWait(bot, 50).until(
        EC.element_to_be_clickable(find_pass_field))
    pass_field.send_keys(PASSWORD)
    bot.find_element_by_xpath(
        '/html/body/div[1]/section/main/article/div/div/div/form/div[1]/div[6]/button').click()
    time.sleep(5)

    link = 'https://www.instagram.com/{}/'.format(usr)
    bot.get(link)
    time.sleep(5)

    bot.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/ul/li[2]/a').click()

    time.sleep(3)
    print('Scrapping...')
    for i in range(round(TIME)):
        ActionChains(bot).send_keys(Keys.END).perform()
        time.sleep(3)

        followers = bot.find_elements_by_xpath(
            '//*[@id="react-root"]/section/main/div/ul/div/li/div/div[1]/div[2]/div[1]/a')

        urls = []

        # getting url from href attribute in title
        for i in followers:
            if i.get_attribute('href') != None:
                urls.append(i.get_attribute('href'))
            else:
                continue

    print('Converting...')
    users = []
    for url in urls:
        user = url.replace('https://www.instagram.com/', '').replace('/', '')
        users.append(user)

    print('Saving...')
    f = open('followers.txt', 'w')
    s1 = '\n'.join(users)
    f.write(s1)
    f.close()


scrape(usr)
