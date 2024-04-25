# import time

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# from webdriver_manager.chrome import ChromeDriverManager

from pyppeteer import launch

from playwright.sync_api import sync_playwright

def save_webpage_as_html(url, output_file, selector):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        # Wait for the page to fully load
        page.wait_for_selector(selector)
        element_text = page.inner_text(selector)
        print("Element text:", element_text)
        # Get the HTML content of the page
        html_content = page.content()
        # Save the HTML content to a file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_content)
        browser.close()



async def test_scrape():

    URL = r"https://unisat.io/runes/market"
    
    browser = await launch()

    # Create a new page
    page = await browser.newPage()

    # Navigate to the webpage
    await page.goto('https://example.com')

    # Wait for the entire page to load
    await page.waitForNavigation()

    # Extract the HTML content of the page
    html_content = await page.content()

    # Save the HTML content to a file
    with open('webpage.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Close the browser
    await browser.close()

    # # Setup chrome options
    # chrome_options = Options()
    # # chrome_options.add_argument("--headless")  # Ensure GUI is off
    # # chrome_options.add_argument("--no-sandbox")
    # # chrome_options.add_argument("--disable-dev-shm-usage")

    # # Set path to chromedriver as per your configuration
    # webdriver_service = Service(ChromeDriverManager().install())

    # # Start the browser
    # driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # # Open the webpage
    # driver.get(URL)

    # num_scrolls = 1
    # scroll_pause_time = 1
    # for _ in range(num_scrolls):
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(scroll_pause_time)

    # # Wait for the JavaScript to load the content
    # driver.maximize_window() # For maximizing window
    # # driver.implicitly_wait(5) # gives an implicit wait for 20 seconds
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-container scroll-x radius20 border-015")))

    # # Get the HTML content of the page
    # html_content = driver.page_source

    # # Save the HTML content to a file
    # with open("page_contents.html", "w", encoding="utf-8") as file:
    #     file.write(html_content)

    # # Get the content
    # table_content = driver.find_element(By.ID, "__next")

    # # Print the dynamic content
    # print(table_content)

    # # Save
    # soup = BeautifulSoup(table_content, features="html.parser")

    # with open("saved_page.html", "w", encoding="utf-8") as file:
    #     file.write(str(soup))

    # Close the browser
    # driver.quit()

    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # wait = WebDriverWait(driver, 10)
    # driver.get(URL)
    
    # # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flex-column align-end gap-2")))

    # prices = driver.find_elements(By.CLASS_NAME, "flex-column align-end gap-2")

    # print(prices)
    
    # wait = WebDriverWait(driver, 10)
    # driver.get(URL)
    # get_url = driver.current_url
    # wait.until(EC.url_to_be(URL))
    # dynamic_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "flex-column align-end gap-2")))

    # if get_url == URL:
    #     page_source = driver.page_source

    # soup = BeautifulSoup(page_source, features="html.parser")

    # with open("saved_page.html", "w", encoding="utf-8") as file:
    #     file.write(str(soup))

