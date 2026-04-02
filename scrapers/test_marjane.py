from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.get("https://www.marjanemall.ma/telephone-objets-connectes/smartphone-telephone/smartphone")
time.sleep(8)

names  = driver.find_elements(By.CSS_SELECTOR, "h3.text-sm")
prices = driver.find_elements(By.CSS_SELECTOR, "span.text-lg")
links  = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")

print(f"Noms: {len(names)} | Prix: {len(prices)} | Liens: {len(links)}")
print("\n=== 5 premiers produits ===")
for i in range(min(5, len(names))):
    nom   = names[i].text.strip()
    prix  = prices[i].text.strip() if i < len(prices) else "N/A"
    lien  = links[i].get_attribute("href") if i < len(links) else "N/A"
    print(f"\n{i+1}. NOM  : {nom}")
    print(f"   PRIX : {prix}")
    print(f"   URL  : {lien}")

driver.quit()