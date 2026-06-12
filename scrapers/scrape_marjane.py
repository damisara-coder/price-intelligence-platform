from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

urls = [
    ("https://www.marjanemall.ma/telephone-objets-connectes/smartphone-telephone/smartphone", "smartphones"),
    ("https://www.marjanemall.ma/tv-son-photo/tv-home-cinema/televiseur", "tv"),
    ("https://www.marjanemall.ma/informatique-gaming/ordinateur/ordinateur-portable", "laptops"),
]
all_products = []

for url, category in urls:
    driver.get(url)
    time.sleep(15)  # attendre plus longtemps

    # Scroll pour charger tous les produits
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    names = driver.find_elements(By.CSS_SELECTOR, "h3.text-sm")
    prices = driver.find_elements(By.CSS_SELECTOR, "span.text-lg")
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")

    print(f"Debug {category}: noms={len(names)}, prix={len(prices)}, liens={len(links)}")

    for i in range(len(names)):
        all_products.append({
            "name": names[i].text.strip(),
            "price": prices[i].text.strip() if i < len(prices) else None,
            "category": category,
            "source": "marjane",
            "url": links[i].get_attribute("href") if i < len(links) else None,
            "timestamp": datetime.now().isoformat()
        })

    print(f"✅ {category} : {len(names)} produits")

driver.quit()

output = r"C:\Users\hp\Desktop\price-intelligence-platform\scrapers\data\marjane.json"
with open(output, 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"\n🎉 Total: {len(all_products)} produits sauvegardés!")
