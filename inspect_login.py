"""Script temporal para inspeccionar el HTML real del login del portal FACTO."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

BASE_URL = "https://com-nt-group-emision-facto-hospitality-front-1016175229083.us-central1.run.app"

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=opts)
try:
    # Probar /login
    print("\n=== Probando BASE_URL + /login ===")
    driver.get(f"{BASE_URL}/login")
    time.sleep(5)
    print("URL final:", driver.current_url)
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"INPUTS: {len(inputs)}")
    for el in inputs:
        print(f"  type={el.get_attribute('type')!r} id={el.get_attribute('id')!r}")
    print("TITLE:", driver.title)
    body = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
    print("HTML snippet:", body[:500])

    # Probar root /
    print("\n=== Probando BASE_URL raiz ===")
    driver.get(f"{BASE_URL}/")
    time.sleep(5)
    print("URL final:", driver.current_url)
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"INPUTS: {len(inputs)}")
    for el in inputs:
        print(f"  type={el.get_attribute('type')!r} id={el.get_attribute('id')!r}")
finally:
    driver.quit()


    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"=== INPUTS encontrados: {len(inputs)}")
    for i, el in enumerate(inputs):
        print(
            f"  input[{i}] "
            f"type={el.get_attribute('type')!r} "
            f"id={el.get_attribute('id')!r} "
            f"name={el.get_attribute('name')!r} "
            f"placeholder={el.get_attribute('placeholder')!r} "
            f"formcontrolname={el.get_attribute('formcontrolname')!r} "
            f"class={el.get_attribute('class')!r}"
        )

    btns = driver.find_elements(By.TAG_NAME, "button")
    print(f"=== BOTONES encontrados: {len(btns)}")
    for i, el in enumerate(btns):
        print(
            f"  button[{i}] "
            f"type={el.get_attribute('type')!r} "
            f"id={el.get_attribute('id')!r} "
            f"text={el.text[:80]!r}"
        )

    body_html = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
    print("=== HTML (primeros 4000 chars):")
    print(body_html[:4000])
finally:
    driver.quit()
