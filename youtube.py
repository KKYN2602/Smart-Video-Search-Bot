import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager


def skip_ads(driver, max_wait=30):
    """
    Poll every 1 second for the 'Skip Ad' button and click it if found.
    Stops after max_wait seconds if no skip button appears.
    """
    print("[INFO] Checking for ads to skip...")
    end_time = time.time() + max_wait
    while time.time() < end_time:
        try:
            skip_btn = driver.find_element(By.CLASS_NAME, "ytp-ad-skip-button")
            if skip_btn.is_displayed() and skip_btn.is_enabled():
                skip_btn.click()
                print("[INFO] Ad skipped!")
                return
        except (NoSuchElementException, ElementClickInterceptedException):
            # Skip button not yet present or not clickable
            pass
        time.sleep(1)
    print("[INFO] No skippable ads detected or timeout reached.")


def search_and_play_youtube_video(query="lofi hip hop"):
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--start-maximized")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        wait = WebDriverWait(driver, 15)

        driver.get("https://www.youtube.com")

        search_box = wait.until(EC.presence_of_element_located((By.NAME, "search_query")))
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        first_video = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title"))
        )

        video_title = first_video.get_attribute("title")
        video_url = first_video.get_attribute("href")

        print(f"[INFO] Now playing: {video_title} - {video_url}")

        first_video.click()

        # Wait and try skipping ads if they appear
        skip_ads(driver, max_wait=30)

    except Exception as e:
        print(f"[ERROR] Something went wrong: {e}")
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


def on_search_click():
    query = entry.get().strip()
    if not query:
        messagebox.showwarning("Input needed", "Please enter a search term.")
        return
    threading.Thread(target=search_and_play_youtube_video, args=(query,), daemon=True).start()


# Tkinter GUI setup
root = tk.Tk()
root.title("Smart YouTube Video Search Bot")

root.geometry("400x120")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")

label = ttk.Label(frame, text="Enter video name to search on YouTube:")
label.pack(pady=(0, 5))

entry = ttk.Entry(frame, width=50)
entry.pack(pady=(0, 10))
entry.focus()

search_button = ttk.Button(frame, text="Search and Play", command=on_search_click)
search_button.pack()

root.mainloop()
