import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service

TIMEOUT = 15


def save_credentials(username, password):
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")
    print("[Info] - Credentials saved to credentials.txt")


def load_credentials():
    if not os.path.exists('credentials.txt'):
        return None

    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    return None


def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password


def login(bot, username, password):
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(1)

    try:
        element = bot.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        element.click()
    except NoSuchElementException:
        print("[Info] - Instagram did not require to accept cookies this time.")

    print("[Info] - Logging in...")
    username_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(bot, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()

    try:
        WebDriverWait(bot, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
        )
        print("[Info] - Login successful.")
    except TimeoutException:
        print("[Error] - Login failed. Check your credentials or solve any captcha.")
        bot.quit()
        exit(1)


def scrape_followers(bot, username, user_input):
    bot.get(f'https://www.instagram.com/{username}/')
    time.sleep(3.5)

    try:
        WebDriverWait(bot, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers')]"))
        ).click()
    except TimeoutException:
        print(f"[Error] - Could not find followers link for {username}. Account may be private or invalid.")
        return

    time.sleep(2)
    print(f"[Info] - Scraping followers for {username}...")

    users = set()
    no_new_count = 0

    while len(users) < user_input:
        followers = bot.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")

        old_count = len(users)
        for i in followers:
            href = i.get_attribute('href')
            if href:
                users.add(href.split("/")[3])

        if len(users) == old_count:
            no_new_count += 1
        else:
            no_new_count = 0

        if no_new_count >= 5:
            print(f"[Info] - No more followers to load. Got {len(users)} out of {user_input} requested.")
            break

        dialog = bot.find_element(By.XPATH, "//div[@role='dialog']")
        ActionChains(bot).scroll_to_element(dialog.find_element(By.XPATH, ".//*[last()]")).perform()
        time.sleep(1)

    users = list(users)[:user_input]

    print(f"[Info] - Saving {len(users)} followers for {username}...")
    with open(f'{username}_followers.txt', 'w') as file:
        file.write('\n'.join(users) + "\n")


def scrape():
    credentials = load_credentials()

    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    user_input = int(input('[Required] - How many followers do you want to scrape (100-2000 recommended): '))

    usernames = input("Enter the Instagram usernames you want to scrape (separated by commas): ").split(",")

    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=service, options=options)
    bot.set_page_load_timeout(TIMEOUT)

    login(bot, username, password)

    for user in usernames:
        user = user.strip()
        scrape_followers(bot, user, user_input)

    bot.quit()


if __name__ == '__main__':
    scrape()
