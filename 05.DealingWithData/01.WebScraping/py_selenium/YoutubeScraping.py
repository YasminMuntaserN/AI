from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from tabulate import tabulate
import time

def get_youtube_channel_data():
    channel = input("What channel are you looking for? (username or handle) ")
    
    options = ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(f"https://www.youtube.com/@{channel}/videos")
        time.sleep(5)  # wait for page to load
        
        videos = driver.find_elements(By.ID, "video-title")
        metadata_list = driver.find_elements(By.ID, "metadata-line")
        
        results = []
        for video, metadata in zip(videos, metadata_list):
            title = video.text
            url = video.get_attribute("href")
            
            spans = metadata.find_elements(By.TAG_NAME, "span")
            views = spans[0].text if len(spans) > 0 else "N/A"
            publish_date = spans[1].text if len(spans) > 1 else "N/A"
            
            results.append([title, url, views, publish_date])
        
        print(tabulate(results, headers=["Title", "URL", "Views", "Publish Date"], tablefmt="fancy_grid"))
    
    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

get_youtube_channel_data()