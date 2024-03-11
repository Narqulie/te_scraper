import time
import json
import logging
from playwright.sync_api import Playwright, sync_playwright, expect

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

alueet = "Tammela"
url = f"https://paikat.te-palvelut.fi/tpt/?locations={alueet}&announced=0&leasing=0&remotely=0&english=false&sort=1"


def save_to_json(data, filename='data.json'):
    """Saves data to a JSON file, appending to it if it already exists."""
    try:
        with open(filename, 'r+', encoding='utf-8') as f:
            file_data = json.load(f)  # Load existing data
            file_data.append(data)  # Append new data
            f.seek(0)  # Reset file position
            json.dump(file_data, f, indent=4, ensure_ascii=False)  # Write updated data
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([data], f, indent=4, ensure_ascii=False)  # Create new file if not exists


def run(playwright: Playwright) -> None:
    """Scrapes job advertisements from a specified URL and saves them to a JSON file."""
    counter = 1  # Initialize counter for ad count
    browser = playwright.chromium.launch(headless=True)  # Launch browser in headless mode for background execution
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    time.sleep(1)  # Wait for page to load

    # Select sorting option on the page
    page.get_by_label("Valitse järjestys").select_option("2")
    time.sleep(1)
    logging.info("Navigated to first page")

    # Click on the first job ad to start the process
    page.locator(".list-group-item").first.click()
    logging.info("Accessing first ad details")

    # Extract and save first ad's details
    page.get_by_text("Kuvaus").click()
    ad_name = page.inner_text(".detailAdName")
    detail_text = page.inner_text(".detailText")
    page.get_by_text("Tiedot").click()
    full_page_html = page.inner_html("html")
    print(full_page_html)

    ad_data = {"Ad count": counter, "Ad Name": ad_name, "Detail Text": detail_text
    save_to_json(ad_data)

    # Iterate through ads using the next button
    next_button = page.locator('[aria-label="Seuraava"]').nth(1)
    while next_button:
        counter += 1
        next_button.first.click()
        ad_name = page.inner_text(".detailAdName")
        detail_text = page.inner_text(".detailText")
        ad_data = {"Ad count": counter, "Ad Name": ad_name, "Detail Text": detail_text}
        save_to_json(ad_data)
        logging.info(f"Processed ad count: {counter}")
        
        # Check if the next button is still present
        element_count = page.locator('[aria-label="Seuraava"]').count()
        if element_count == 0:
            logging.info("Next button not present. Ending process.")
            break

    context.close()
    browser.close()

# Run the script using Playwright
with sync_playwright() as playwright:
    run(playwright)
