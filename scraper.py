from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
username='email'
password='password'
job_keyword="Data Scientist"
# Define options to make Selenium lightweight
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument('--no-sandbox')
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
driver.get('https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin')
user_field = driver.find_element("id","username")
pw_field = driver.find_element("id","password")
login_button = driver.find_element("xpath",
            '//*[@id="organic-div"]/form/div[3]/button')
user_field.send_keys(username)
user_field.send_keys(Keys.TAB)
time.sleep(2)
pw_field.send_keys(password)
time.sleep(2)
login_button.click()
time.sleep(6)
#minimize=driver.find_element("id","ember150")
#minimize.click()
search_button = driver.find_element(By.CLASS_NAME,"search-global-typeahead")
# Use ActionChains to perform a right-click on the search button element and choose "Inspect"
actions = ActionChains(driver)
actions.click(search_button).perform()
actions.send_keys(job_keyword).perform()
actions.send_keys(Keys.ENTER).perform()
time.sleep(6)
# Wait for the search bar to load and type "data scientist" into it
jobsicon = driver.find_element(By.CSS_SELECTOR, "button[class*='search-reusables__']")
jobsicon.click()
time.sleep(6)
scrollresults = driver.find_element(By.CLASS_NAME,
    "jobs-search-results-list"
)
for i in range(300, 5000, 100):
   driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollresults)
   time.sleep(0.2)
links = driver.find_elements("xpath",
    '//div[@data-job-id]'
)

jobs_df = pd.DataFrame(columns=['Job Title', 'Location', 'Applicant Count', 'Job Poster', 'Requirements', 'Job URL'])
page_num=2
while True:
    links = driver.find_elements("xpath",'//div[@data-job-id]')
    for i in range(len(links)):
        try:
            link=links[i]
            link.click()
            time.sleep(1)
            if f"{job_keyword}" not in driver.title:
                driver.back()
                time.sleep(4)
                links = driver.find_elements("xpath",'//div[@data-job-id]')
            else:
                pass
            link=links[i]
            html_source = link.get_attribute('innerHTML')

            # create a BeautifulSoup object from the HTML source
            soup = BeautifulSoup(html_source, 'html.parser')

            # extract the job title, company name, and location from the soup object
            try:
                job_title = soup.find('a', {'class': 'disabled ember-view job-card-container__link job-card-list__title'}).text.strip()
            except AttributeError:
                job_title = None

            try:
                element = driver.find_element(By.CSS_SELECTOR, f'div[aria-label="{job_title}"][data-job-details-events-trigger=""]')
                soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')

                location = soup.find('span', {'class': 'jobs-unified-top-card__bullet'}).text.strip()
            except:
                location = None

            try:
                applicant_count = int(soup.find('span', {'class': 'jobs-unified-top-card__applicant-count'}).text.strip().split()[0])
            except (AttributeError, ValueError):
                applicant_count = None

            try:
                job_poster = soup.find('span', {'class': 'jobs-poster__name'}).strong.text.strip()
            except AttributeError:
                job_poster = None

            try:
                requirement_tags = soup.find('div', {'id': 'job-details'}).find_all('li')
                requirements = [tag.text.strip() for tag in requirement_tags if tag.text.strip()]

                for tag in requirement_tags:
                    if not tag.text.strip():
                        tag.decompose()
                    else:
                        tag.contents[0].replace_with(tag.text.strip())
            except AttributeError:
                requirements = None

            try:
                job_url = "https://www.linkedin.com/" + soup.find('a')['href']
            except (AttributeError, TypeError):
                job_url = None

            jobs_df.loc[jobs_df.shape[0]] = {
                'Job Title': job_title,
                'Location': location,
                'Applicant Count': applicant_count,
                'Job Poster': job_poster,
                'Requirements': requirements,
                'Job URL': job_url
            }
            
            time.sleep(1)
        except: print('Whoopsidaisy')
    
    jobs_df.to_csv("jobs.csv")
    
    try:
        # find the Next button using selenium By
        next_button = driver.find_element(By.XPATH, "//button[@aria-label='Page " + str(page_num + 1) + "']")
        next_button.click()
        time.sleep(2)  # wait for page to load
        page_num += 1  # update page number
        scrollresults = driver.find_element(By.CLASS_NAME,"jobs-search-results-list")
        for i in range(300, 5000, 100):
            driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollresults)
            time.sleep(0.2)
        print(page_num)
    except:
        # stop loop if no more Next button available
        break
