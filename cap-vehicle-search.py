from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import csv

#working, generates clean csv with proper headers and the first pic of each car. 

#Can be used to return a txt or html file containing data about cars on lot at Chesterfield Auto Parts. The idea is that that I can be automatically alerted
#via bot or email when a vehicle I'm interested in hits the lot. 

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensures the browser runs in headless mode
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the URL
url = "https://chesterfieldauto.com/search-our-inventory-by-location?SelectedMake.Id=318" #the ID in URL is for the make, later I can modity this, but you can get a different ID by visiting the site and selecting the make and then use that URL
driver.get(url)
driver.set_window_size(1550, 830)

# Interact with the model dropdown
dropdown = driver.find_element(By.ID, "selected-model")
dropdown.click()
vibe_option = dropdown.find_element(By.XPATH, "//option[. = 'Vibe']")
vibe_option.click()

# Interact with the 'Begin Year' field
begin_year = driver.find_element(By.ID, "BasicSearch_BeginYear")
begin_year.clear()
begin_year.send_keys("2002")

# Interact with the 'End Year' field
end_year = driver.find_element(By.ID, "BasicSearch_EndYear")
end_year.clear()
end_year.send_keys("2010")

# Click the primary button to perform the search
search_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
search_button.click()

#verifify the table content containing the vehicle data has loaded
wait = WebDriverWait(driver, 5)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody > tr")))

# Retrieve and save the page source to file
rendered_html = driver.page_source
with open('page_source.html', 'w', encoding='utf-8') as file: 
    file.write(rendered_html)

# Close the browser
driver.quit()

with open('page_source.html', 'r', encoding='utf-8') as file:
    page_content = file.read()

soup = BeautifulSoup(page_content, "html.parser")

# Extracting headers and adding 'Pic' at the end
headers = [th.text.strip() for th in soup.find_all("th") if th.text.strip() != 'Pics']
headers.append('Pic')  # Rename 'Pics' to 'Pic' and move it to the end

# Process each row in the <tbody> of the table
table_data = []
tbody = soup.find("tbody")
if tbody:
    for tr in tbody.find_all("tr"):
        row_data = []
        pic_url = "No image"  # Default if no image is found

        for td in tr.find_all("td"):
            # Extracting the data-target from the button for image URL
            button = td.find("button")
            if button and "data-target" in button.attrs:
                data_target = button["data-target"].strip("#")
                modal = soup.find("div", id=data_target)
                if modal:
                    image_tags = modal.find_all("img")
                    if image_tags:
                        pic_url = image_tags[0]["src"]  # Get the first image URL
            else:
                # Extracting regular table data
                row_data.append(td.get_text(strip=True))

        # Append the picture URL to the end of row data
        row_data.append(pic_url)
        table_data.append(row_data)

# Write the data to a CSV file
with open("vehicles.csv", "w", newline="", encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the headers
    writer.writerows(table_data)  # Write the table data