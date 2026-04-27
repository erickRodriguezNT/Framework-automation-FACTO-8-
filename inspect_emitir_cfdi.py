"""
inspect_emitir_cfdi.py - Script para inspeccionar el dropdown del botón
"Emitir CFDI" en el portal FACTO autenticado.
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://com-nt-group-emision-facto-hospitality-front-1016175229083.us-central1.run.app/"
USERNAME = "desarrollo.nt@next-technologies.com.mx"
PASSWORD = "gL490+.r"

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    # --- Login ---
    driver.get(BASE_URL)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(
        By.XPATH,
        "//button[@type='submit' and not(@aria-hidden='true') and normalize-space(.)='Continuar']"
    ).click()
    WebDriverWait(driver, 30).until(lambda d: "auth0.com" not in d.current_url)
    time.sleep(8)  # Esperar Angular
    print(f"Logueado. URL: {driver.current_url}")

    # --- Hacer click en "Emitir CFDI" ---
    print("\n1. Buscando botón 'Emitir CFDI'...")
    emitir_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[normalize-space(text())='Emitir CFDI']]")
        )
    )
    print(f"   Botón encontrado: {emitir_btn.get_attribute('class')[:80]}")
    emitir_btn.click()
    print("   Click realizado en 'Emitir CFDI'")
    time.sleep(2)

    # --- Guardar HTML post-click ---
    os.makedirs("reports", exist_ok=True)
    with open("reports/emitir_cfdi_dropdown.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("   HTML guardado en: reports/emitir_cfdi_dropdown.html")

    # --- Ver texto visible ---
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"\n2. Texto visible tras click:\n{'='*50}")
    print(body_text[:2000])
    print("="*50)

    # --- Buscar ítems del dropdown ---
    print("\n3. Buscando ítems del dropdown...")
    # Buscar nuevos elementos con texto de módulos
    all_clickable = driver.find_elements(By.CSS_SELECTOR, "a, button, [role='menuitem'], [role='option'], li")
    for el in all_clickable:
        txt = el.text.strip()
        if any(kw in txt.lower() for kw in ["factura", "nota", "ppd", "complemento", "adenda", "pago"]):
            tag = el.tag_name
            cls = el.get_attribute("class") or ""
            href = el.get_attribute("href") or ""
            print(f"   <{tag}> text='{txt[:60]}' class='{cls[:60]}' href='{href}'")

    # --- Buscar específicamente Factura en el dropdown ---
    print("\n4. Buscando 'Factura' o 'Facturación' directo...")
    xpaths = [
        "//a[contains(normalize-space(.), 'Factura')]",
        "//button[contains(normalize-space(.), 'Factura')]",
        "//*[contains(@class,'dropdown')]//a",
        "//*[contains(@class,'popup')]//a",
        "//*[contains(@class,'menu')]//a",
    ]
    for xp in xpaths:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            print(f"   XPath '{xp}' encontró {len(els)} elementos:")
            for el in els[:5]:
                print(f"     text='{el.text.strip()[:60]}' href='{el.get_attribute('href')}'")

    input("\nPresiona Enter para cerrar el navegador...")

finally:
    driver.quit()
    print("Driver cerrado.")
