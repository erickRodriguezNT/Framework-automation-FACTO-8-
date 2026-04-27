"""
inspect_receptor.py - Inspecciona el formulario del receptor en la pantalla
de factura para descubrir los selectores reales del componente app-receptor-factura.
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
    driver.find_element(By.XPATH, "//button[@type='submit' and not(@aria-hidden='true') and normalize-space(.)='Continuar']").click()
    WebDriverWait(driver, 30).until(lambda d: "auth0.com" not in d.current_url)
    time.sleep(8)
    print(f"Logueado. URL: {driver.current_url}")

    # --- Navegar a Factura ---
    print("\n1. Abriendo menú 'Emitir CFDI'...")
    emitir_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space(text())='Emitir CFDI']]"))
    )
    emitir_btn.click()
    time.sleep(1)
    factura_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space(text())='Factura']]"))
    )
    factura_btn.click()
    time.sleep(4)
    print(f"   URL: {driver.current_url}")

    # --- Llenar RFC para activar el formulario completo ---
    print("\n2. Llenando RFC para activar el formulario...")
    rfc_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "app-receptor-factura input[placeholder='ABC010101XXX']"))
    )
    rfc_input.clear()
    rfc_input.send_keys("XAXX010101000")
    time.sleep(1)

    # Click botón búsqueda
    buscar_btn = driver.find_element(By.CSS_SELECTOR, "app-receptor-factura button[type='button']")
    buscar_btn.click()
    time.sleep(2)

    # Llenar razón social y CP
    try:
        rs = driver.find_element(By.CSS_SELECTOR, "app-receptor-factura input[placeholder='NOMBRE O DENOMINACIÓN SOCIAL']")
        rs.clear()
        rs.send_keys("PUBLICO EN GENERAL")
        time.sleep(0.5)
    except Exception as e:
        print(f"   [WARN] Razón social: {e}")

    try:
        cp = driver.find_element(By.CSS_SELECTOR, "app-receptor-factura input[placeholder='00000']")
        cp.clear()
        cp.send_keys("00000")
        time.sleep(0.5)
    except Exception as e:
        print(f"   [WARN] CP: {e}")

    time.sleep(2)

    # --- Guardar HTML del componente receptor ---
    print("\n3. Inspeccionando app-receptor-factura...")
    os.makedirs("reports", exist_ok=True)
    with open("reports/receptor_form.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("   HTML guardado en: reports/receptor_form.html")

    # --- Inspeccionar selects dentro del componente ---
    receptor = driver.find_element(By.CSS_SELECTOR, "app-receptor-factura")
    selects = receptor.find_elements(By.TAG_NAME, "select")
    print(f"\n4. Selects encontrados en app-receptor-factura: {len(selects)}")
    for i, sel in enumerate(selects):
        sel_id = sel.get_attribute("id") or ""
        sel_name = sel.get_attribute("name") or ""
        sel_class = sel.get_attribute("class") or ""
        sel_formcontrol = sel.get_attribute("formcontrolname") or sel.get_attribute("ng-reflect-name") or ""
        options_els = sel.find_elements(By.TAG_NAME, "option")
        opts_text = [o.text.strip()[:50] for o in options_els[:5]]
        print(f"\n   select[{i}]:")
        print(f"     id='{sel_id}' name='{sel_name}'")
        print(f"     formcontrolname='{sel_formcontrol}'")
        print(f"     class='{sel_class[:80]}'")
        print(f"     options (primeras 5): {opts_text}")

    # --- Inspeccionar todos los inputs ---
    inputs = receptor.find_elements(By.TAG_NAME, "input")
    print(f"\n5. Inputs encontrados en app-receptor-factura: {len(inputs)}")
    for i, inp in enumerate(inputs):
        inp_type = inp.get_attribute("type") or ""
        inp_placeholder = inp.get_attribute("placeholder") or ""
        inp_id = inp.get_attribute("id") or ""
        inp_formcontrol = inp.get_attribute("formcontrolname") or inp.get_attribute("ng-reflect-name") or ""
        print(f"   input[{i}]: type='{inp_type}' placeholder='{inp_placeholder}' id='{inp_id}' formcontrolname='{inp_formcontrol}'")

    # --- HTML del componente ---
    print("\n6. HTML interno de app-receptor-factura:")
    inner_html = receptor.get_attribute("innerHTML")
    print(inner_html[:4000])

    input("\nPresiona Enter para cerrar...")

finally:
    driver.quit()
    print("Driver cerrado.")
