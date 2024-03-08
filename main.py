from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re

# Configure Selenium WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

data = []


def extract_details(details_divs):
    details = {
        "Rocket_Status": "N/A",
        "Price": "N/A",
        "Liftoff Thrust": "N/A",
        "Payload to LEO": "N/A",
        "Payload to GTO": "N/A",
        "Stages": "N/A",
        "Strap-ons": "N/A",
        "Rocket Height": "N/A",
        "Fairing Diameter": "N/A",
        "Fairing Height": "N/A",
    }
    for div in details_divs:
        text = div.text
        if "Status:" in text:
            details["Rocket_Status"] = text.split("Status:")[-1].strip()
        elif "Price:" in text:
            details["Price"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Liftoff Thrust:" in text:
            details["Liftoff Thrust"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Payload to LEO:" in text:
            details["Payload to LEO"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Payload to GTO:" in text:
            details["Payload to GTO"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Stages:" in text:
            details["Stages"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Strap-ons:" in text:
            details["Strap-ons"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Rocket Height:" in text:
            details["Rocket Height"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Fairing Diameter:" in text:
            details["Fairing Diameter"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )
        elif "Fairing Height:" in text:
            details["Fairing Height"] = (
                re.search(r"\d+\.?\d*", text).group()
                if re.search(r"\d+\.?\d*", text)
                else "N/A"
            )

    return details


def get_mission_status():
    try:
        mission_status_element = driver.find_element(
            By.XPATH, "/html/body/div/div/main/div/section[1]/h6/span"
        )
        return mission_status_element.text.strip()
    except NoSuchElementException:
        return "N/A"


driver.get("https://nextspaceflight.com/launches/past/?search=")
try:
    while True:

        # Wait for the dynamic content to load and scroll to the bottom
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "launch")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.launch:last-child"))
        )

        for card in driver.find_elements(By.CLASS_NAME, "launch"):
            # Extracting details using Selenium directly
            organization = card.find_element(
                By.CSS_SELECTOR, "span[style*='color: black']"
            ).text.strip()
            detail = card.find_element(By.CSS_SELECTOR, "h5.header-style").text.strip()
            date_location_text = card.find_element(
                By.CSS_SELECTOR, "div.mdl-card__supporting-text"
            ).text.strip()
            date, location = (
                date_location_text.split("\n")
                if "\n" in date_location_text
                else ("N/A", "N/A")
            )

            card.find_element(
                By.CSS_SELECTOR, "a.mdc-button[href*='/launches/details']"
            ).click()
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/div/main/div/section[2]/div/div[1]/div")
                )
            )

            # Locate the larger div using XPath
            details_container = driver.find_element(
                By.XPATH, "/html/body/div/div/main/div/section[2]/div/div[1]/div"
            )

            # Find all child div elements within the located container
            details_divs = details_container.find_elements(
                By.CSS_SELECTOR, "div.mdl-cell"
            )
            launch_details = extract_details(details_divs)

            mission_status = get_mission_status()

            data.append(
                {
                    "Organization": organization,
                    "Location": location,
                    "Date": date,
                    "Detail": detail,
                    **launch_details,
                    "mission_status": mission_status,
                }
            )

            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "launch")))

        next_page_button = driver.find_elements(
            By.XPATH, "/html/body/div/div/main/div/div[2]/div[2]/span/div/button[1]"
        )
        if next_page_button and "disabled" not in next_page_button[0].get_attribute(
            "class"
        ):
            next_page_button[0].click()
        else:
            break

except NoSuchElementException:
    print(
        "An element was not found. This might be due to a change in the website's structure."
    )
except TimeoutException:
    print("Page took too long to load and timed out.")
except WebDriverException as e:
    print(f"WebDriver encountered an issue: {e}")
finally:
    df = pd.DataFrame(data)
    # Add a index
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Unnamed: 0"}, inplace=True)
    csv_filename = "spaceflight_data.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        df.to_csv(file, index=False)
    driver.quit()
    print(f"Data scraped and saved to {csv_filename}")
