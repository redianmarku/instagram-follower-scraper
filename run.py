import os
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM

# Complete these 2 fields ==================
USERNAME = 'your instagram username'
PASSWORD = 'your instagram password'
# ==========================================

TIMEOUT = 15


def scrape():
    usr = input('Whose followers do you want to scrape: ')

    user_input = int(input('How many followers do you want to scrape (60-500 recommended): '))

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")

    bot = webdriver.Chrome(executable_path=CM().install(), options=options)

    bot.get('https://www.instagram.com/accounts/login/')

    time.sleep(2)

    print("Logging in...")

    user_element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')))

    user_element.send_keys(USERNAME)

    pass_element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')))

    pass_element.send_keys(PASSWORD)

    login_button = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div/div[3]')))

    time.sleep(0.4)

    login_button.click()

    time.sleep(5)

    bot.get('https://www.instagram.com/{}/'.format(usr))

    time.sleep(3.5)

    WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a'))).click()

    time.sleep(2)

    followers_elem = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '/html/body/div[5]/div/div/div[2]/ul/div/li[1]')))

    print('Scraping...')

    users = set()

    for _ in range(round(user_input // 10)):
        followers_elem.click()

        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(2)

        followers = bot.find_elements_by_xpath(
            '/html/body/div[5]/div/div/div[2]/ul/div/li/div/div[1]/div/div/a')

        # Getting url from href attribute
        for i in followers:
            if i.get_attribute('href'):
                users.add(i.get_attribute('href').split("/")[3])
            else:
                continue

    mode = "a"

    if os.path.exists("followers.txt"):
        choice = input("You already have a file named 'followers.txt'\n"
                       "Do you want to delete it's content? (y/N): ").lower()
        mode = "w" if choice == "y" else mode

    print('Saving...')

    with open('followers.txt', mode) as file:
        file.write('\n'.join(users) + "\n")

    print("Finished!")


if __name__ == '__main__':
    scrape()
