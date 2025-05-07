import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC



class PropertyScraper:
    
    
    def __init__(self, url, timeout=10):
        self.url = url
        self.data = []
        self.driver = self._initialize_driver()
        self.wait = WebDriverWait(self.driver, timeout=timeout)
    
    
    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-http2")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--enable-features=NetworkServiceInProcess")
        chrome_options.add_argument("--disable-features=NetworkService")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
        )
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        return driver
    
    
    def _wait_for_page_to_load(self):
        title = self.driver.title
    
        try:
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
        except:
            print(f"The webpage \"{title}\" did not get fully loaded.\n")
            
        else:
            print(f"The webpage \"{title}\" did get fully loaded.\n")
    
    
    def access_website(self):
        self.driver.get(self.url)
        self._wait_for_page_to_load()    
    
    
    def search_properties(self, text):
        # Identifying and Entering Text to the Search Bar
        try:
            search_bar = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="keyword2"]'))
            )
        except:
            print("Timeout while locating Search Bar.\n")
        else:
            search_bar.send_keys(text)
            time.sleep(5)
        
        # Selecting the Valid option from the List
        try:
            valid_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="0"]'))
            )
        except:
            print("Timeout while locating valid Search Option.\n")
        else:
            valid_option.click()
            time.sleep(5)
        
        # Click on Search Button
        try:
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="searchform_search_btn"]'))
            )
        except:
            print("Timeout while clicking \"Search\" Button.\n")
        else:
            search_button.click()
            self._wait_for_page_to_load()
    
    
    def adjust_budget_slider(self, offset):
        # Adjust the Budget Slider
        try:
            slider = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="budgetLeftFilter_max_node"]'))
            )
        except:
            print("Timeout while clicking in Budget Slider Circle")
        else:
            actions = ActionChains(self.driver)
            (
                actions
                .click_and_hold(slider)
                .move_by_offset(offset,0)
                .release()
                .perform()
            )
            time.sleep(5)
    
    
    def apply_filters(self):
        # Filter Results

        # 1. Verified
        verified = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[4]/div[3]/div[1]/div[3]/section/div/div/div/div/div[1]/div/div[3]'))
        )
        verified.click()
        time.sleep(2)

        #. 2. Ready To Move
        ready_to_move = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[4]/div[3]/div[1]/div[3]/section/div/div/div/div/div[1]/div/div[5]'))
        )
        ready_to_move.click()
        time.sleep(2)

        # Moving the slider the the right to unhide the remaining filters.

        # For First Scrolling to Right
        filter_right_button_1st = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/div[3]/div[1]/div[3]/section/div/div/div/div/div[2]'))
        )
        filter_right_button_1st.click()
        time.sleep(2)

        # For Second Scrolling to Right
        filter_right_button_2nd = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/div[3]/div[1]/div[3]/section/div/div/div/div/div[3]'))
        )
        filter_right_button_2nd.click()
        time.sleep(2)


        #. 3. With Photos
        with_photos = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[4]/div[3]/div[1]/div[3]/section/div/div/div/div/div[2]/div/div[6]'))
        )
        with_photos.click()
        time.sleep(2)


        #. 4. With Videos
        with_videos = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[4]/div[3]/div[1]/div[3]/section/div/div/div/div/div[2]/div/div[7]'))
        )
        with_videos.click()
        time.sleep(5)
    
    
    def _extract_data(self, row, by, value):
        try:
            return row.find_element(by, value).text
        except:
            return np.nan
    
    
    def scrape_data(self):
        # Scraping Data from the Last Page

        rows = self.driver.find_elements(By.CLASS_NAME, "tupleNew__TupleContent")
        for row in rows:
            
            property = {
                "name" : self._extract_data(row, By.CLASS_NAME, "tupleNew__headingNrera"),
                "location" : self._extract_data(row, By.CLASS_NAME, "tupleNew__propType"),
                "price" : self._extract_data(row, By.CLASS_NAME, "tupleNew__priceValWrap")
            }
            
            # Property Area and BHK
            try:
                elements = row.find_elements(By.CLASS_NAME, "tupleNew__area1Type")
            except:
                property["area"], property["bhk"] = [np.nan, np.nan]
            else:
                property["area"], property["bhk"] = [ele.text for ele in elements]
            
            
            self.data.append(property)
    
    
    def navigate_pages_and_scrape_data(self):
        
        page_count = 0
        while True:
            page_count += 1
            try:
                time.sleep(6)
                self.scrape_data()                
                next_page_button = self.driver.find_element(By.XPATH, "//a[normalize-space()='Next Page >']")
            except:
                print(f"Timeout because we have scraped {page_count} pages.\n")
                break
            else:
                try:
                    self.driver.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 100);", next_page_button)
                    time.sleep(6)

                    self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Next Page >']"))
                    ).click()
                    time.sleep(6)
                
                except:
                    print("Timeout while clicking on \"Next Page\".\n")
    
    
    def data_cleaning_and_exporting(self, file_name):
        df = (
            pd
            .DataFrame(self.data)
            .drop_duplicates()
            .apply(lambda col: col.str.strip().str.lower() if col.dtype == 'object' else col)
            .assign(
                is_reviewed = lambda df_ : (
                        df_
                        .name
                        .str.contains("\n")
                        .astype(int)
                    ),
                name = lambda df_: (
                        df_
                        .name
                        .str.replace("\n[0-9.]+", "", regex=True)
                        .str.strip()
                    ),
                location = lambda df_: (
                        df_
                        .location
                        .str.replace("Kolkata", "") 
                        # ^ We have to change this value according to cleaning.
                        .str.strip()
                        .str.replace(",$", "", regex=True)
                        .str.split("in")
                        .str[-1]
                        .str.strip()
                    ),
                price = lambda df_: (
                        df_
                        .price
                        .str.replace("₹", "")
                        .apply(
                            lambda val: float(val.replace('lac', '').strip()) if 'lac' in val else float(val.replace("cr","").strip()) * 100 
                        )
                    ),
                area = lambda df_: (
                        df_
                        .area
                        .str.replace("sqft", "")
                        .str.strip()
                        .str.replace(",", "")
                        .str.strip()
                        .astype(int)
                    ),
                bhk = lambda df_: (
                        df_
                        .bhk
                        .str.replace("bhk", "")
                        .str.strip()
                        .astype(int)
                    ),
            
            )
            .rename(columns={
                'price': 'price_lacs',
                'area': 'area_sqft'
            })
            .reset_index(drop=True)
        )
        
        df.to_csv(f"{file_name}.csv", index=False)
    
    
    
    def run(self, text = "Kolkata", offset = -100,  file_name = "Properties"):
        try:
            self.access_website()
            self.search_properties(text)
            self.adjust_budget_slider(offset)
            self.apply_filters()
            self.navigate_pages_and_scrape_data()
            self.data_cleaning_and_exporting(file_name)
        finally:
            time.sleep(5)
            self.driver.quit()



if __name__ == "__main__":
    scraper = PropertyScraper(url = "https://www.99acres.com/")
    scraper.run(
        text = "kolkata",
        offset= -73,
        file_name= "kolkata-properties-cleaned"
    )