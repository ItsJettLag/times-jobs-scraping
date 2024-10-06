# Import necessary libraries for web scraping, parsing, data handling, and time management
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time

# Set up the Selenium WebDriver (Chrome in headless mode)
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no UI)
    driver = webdriver.Chrome(options=options)
    return driver

# Close any pop-ups that might appear on the TimesJobs website
def close_popup(driver):
    try:
        # Wait for the pop-up to be clickable, then close it
        pop_up = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/table/tbody/tr/td[2]/div/span'))
        )
        pop_up.click()
        print("Pop-up closed successfully.")
    except Exception as e:
        print(f"Failed to close pop-up: {e}")

# Parse job listings from the current page using BeautifulSoup
def parse_job_listings(driver):
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    job_list = soup.find('ul', class_='new-joblist')
    job_items = job_list.find_all('li', class_='clearfix job-bx wht-shd-bx') if job_list else []
    return job_items

# Extract details for each job listing (title, company, experience, etc.)
def extract_job_details(job_item):
    try:
        title = job_item.find('a').text.strip().replace('"', '').title()
    except AttributeError:
        title = "Title not found"
    
    try:
        company = job_item.find('h3', class_='joblist-comp-name').text.strip().title()
        company = company.replace("(More Jobs)", "").strip()
    except AttributeError:
        company = "Company not found"
    
    try:
        exp = job_item.find('i', class_='material-icons').next_sibling.strip()
    except AttributeError:
        exp = "Experience not found"
    
    try:
        city = job_item.find('span', title=True).text.strip()
        city = city.replace("Bengaluru / Bangalore", "Bangalore").replace("null,", "")
    except AttributeError:
        city = "City not found"
    
    try:
        date = job_item.find('span', class_='sim-posted').text.strip()
    except AttributeError:
        date = "Date not found"
    
    try:
        skills = job_item.find('span', class_='srp-skills').text.strip()
        skills_list = [skill.strip() for skill in skills.split(',')]
        skills = ', '.join(skills_list)
    except AttributeError:
        skills = "Skills not found"
    
    try:
        job_url = job_item.find('a').get('href').strip()
    except AttributeError:
        job_url = "URL not found"
    
    return {
        'Title': title,
        'Company': company,
        'Experience': exp,
        'City': city,
        'Date Posted': date,
        'Skills': skills,
        'URL': job_url
    }

# Save the scraped data to an Excel file with a timestamp
def save_to_excel(dataframe):
    current_time = datetime.datetime.now().strftime("%H-%M")
    filename = f"TimesJobs_Scraped_{current_time}.xlsx"
    dataframe.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

# Main function to handle scraping, page navigation, and saving the data
def main():
    # Initialize an empty DataFrame to store job listings
    dff = pd.DataFrame(columns=['Title', 'Company', 'Experience', 'City', 'Date Posted', 'Skills', 'URL'])
    driver = setup_driver()  # Start the WebDriver
    
    # Base URL for the job listings (TimesJobs with Big Data keyword)
    base_url = 'https://www.timesjobs.com/candidate/job-search.html?from=submit&luceneResultSize=25&txtKeywords=0DQT0Big%20Data0DQT0&postWeek=60&searchType=personalizedSearch&actualTxtKeywords=0DQT0Big%20Data0DQT0&searchBy=0&rdoOperator=OR&txtLocation=india&pDate=I&sequence={}&startPage=1'
    
    close_popup(driver)  # Close any pop-ups before scraping
    
    job_count = 0  # Track number of jobs scraped
    desired_job_count = 1000  # Target number of job listings to scrape
    page_number = 1  # Start at page 1
    retries = 0  # Retry counter for error handling
    max_retries = 3  # Maximum number of retries allowed

    # Loop through pages until desired job count is reached or retries are exhausted
    while job_count < desired_job_count and retries < max_retries:
        driver.get(base_url.format(page_number))
        time.sleep(2)  # Wait for the page to load
        
        job_items = parse_job_listings(driver)
        if not job_items:
            print(f"No jobs found on page {page_number}. Retrying ({retries + 1}/{max_retries}).")
            retries += 1
            continue
        
        retries = 0  # Reset retries after a successful page fetch
        
        for job_item in job_items:
            job_details = extract_job_details(job_item)
            dff = pd.concat([dff, pd.DataFrame([job_details])], ignore_index=True)
            job_count += 1
            if job_count >= desired_job_count:
                break
        
        page_number += 1  # Go to the next page

    save_to_excel(dff)  # Save the final data to Excel
    
    # Password-protected driver closing (user must input the correct password)
    correct_password = "Warda313@"
    print("Browser will stay open. Enter the password to close it.")

    while True:
        user_input = input("Enter password to close the browser: ")
        if user_input == correct_password:
            print("Correct password entered. Closing the browser...")
            break
        else:
            print("Incorrect password. Try again.")

    driver.quit()  # Close the WebDriver

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
