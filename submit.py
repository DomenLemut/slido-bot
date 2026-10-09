from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BUTTON2_IDS = [
    "a97268cf-4aca-4149-8209-b12f71d73407",
    "244e82a4-d890-4357-b091-cd3c5880b61a",
    "046102a1-a8f0-4b19-95f3-599359122f41",
]

SUBMIT_ID = "poll-submit-button"
URL = "https://app.sli.do/event/kvuAavKoMDe9RLQZSfHB1Y"
BUTTON1_ID = "633f34c4-a5ae-48b6-8e28-177ed29074f8"
TOTAL_RUNS = 100000
MAX_WORKERS = 14  # Adjust higher (e.g., 12 or 16) if your hardware/CPU can handle it
MAX_RETRIES = 3  # Automatically retry failed votes up to 3 times


def perform_vote(run_index):
  options = webdriver.ChromeOptions()
  options.add_argument("--incognito")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--headless=new")
  options.add_argument("--disable-gpu")
  options.add_argument("--disable-extensions")
  options.add_argument("--blink-settings=imagesEnabled=false")

  # --- MAX SPEED FLAGS ---
  options.page_load_strategy = (
      "eager"  # Don't wait for heavy assets; fire as soon as DOM is ready
  )
  options.add_argument(
      "--disable-site-isolation-trials"
  )  # Cuts massive CPU/RAM overhead per thread
  options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
  options.add_argument("--disable-logging")
  options.add_argument("--log-level=3")

  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option("useAutomationExtension", False)

  # Reliability: Attempt with retries if a network blip occurs
  for attempt in range(1, MAX_RETRIES + 1):
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)

    try:
      driver.get(URL)
      wait = WebDriverWait(driver, 4)  # Tighter wait window for speed

      # Click Button 1
      btn1 = wait.until(EC.element_to_be_clickable((By.ID, BUTTON1_ID)))
      btn1.click()

      # Click Button 2
      btn2_id = BUTTON2_IDS[random.randint(0, len(BUTTON2_IDS) - 1)]
      btn2 = wait.until(EC.element_to_be_clickable((By.ID, btn2_id)))
      btn2.click()

      # Submit Vote
      submit_btn = wait.until(EC.element_to_be_clickable((By.ID, SUBMIT_ID)))
      submit_btn.click()

      # Success - clean up browser and return True
      driver.quit()
      return True

    except Exception as e:
      try:
        driver.quit()
      except:
        pass

      if attempt == MAX_RETRIES:
        # Failed permanently after max retries
        return False
      else:
        # Brief backoff before retrying
        time.sleep(0.3 * attempt)

  return False


if __name__ == "__main__":
  print(
      f"🚀 Starting max-speed automation: {MAX_WORKERS} workers,"
      f" {TOTAL_RUNS} total runs."
  )

  success_count = 0
  fail_count = 0
  start_time = time.time()

  with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(perform_vote, i + 1): i + 1
        for i in range(TOTAL_RUNS)
    }

    for future in as_completed(futures):
      if future.result():
        success_count += 1
      else:
        fail_count += 1

      # Print live progress update every 100 completed runs
      total_done = success_count + fail_count
      if total_done % 100 == 0:
        elapsed = time.time() - start_time
        rate = total_done / elapsed if elapsed > 0 else 0
        print(
            f"📊 Progress: {total_done}/{TOTAL_RUNS} | Success:"
            f" {success_count} | Failed: {fail_count} | Speed: {rate:.2f}"
            " votes/sec"
        )

  print(
      "🏁 Finished! Total Success:"
      f" {success_count}, Total Failed: {fail_count}"
  )