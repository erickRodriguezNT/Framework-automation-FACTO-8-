"""
inspect_menu.py - Script de diagnóstico para inspeccionar el HTML
del portal FACTO después de autenticarse, para descubrir los
selectores reales del menú de navegación.

Uso:
    python inspect_menu.py
"""
import time
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
    print("1. Navegando al portal...")
    driver.get(BASE_URL)
    time.sleep(5)

    print(f"   URL actual: {driver.current_url}")
    print(f"   Título: {driver.title}")

    # Ingresar email
    print("2. Ingresando email...")
    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    email_input.clear()
    email_input.send_keys(USERNAME)

    # Ingresar contraseña
    print("3. Ingresando contraseña...")
    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(PASSWORD)

    # Click "Continuar"
    print("4. Haciendo click en Continuar...")
    btn = driver.find_element(
        By.XPATH,
        "//button[@type='submit' and not(@aria-hidden='true') and normalize-space(.)='Continuar']"
    )
    btn.click()

    # Esperar redirección al portal
    print("5. Esperando redirección al portal...")
    WebDriverWait(driver, 30).until(
        lambda d: "auth0.com" not in d.current_url
    )
    print(f"   URL tras login: {driver.current_url}")
    print(f"   Título: {driver.title}")

    # Esperar que Angular cargue el portal completamente
    print("6. Esperando que Angular cargue el portal (10 segundos)...")
    time.sleep(10)
    print(f"   URL final: {driver.current_url}")
    print(f"   Título final: {driver.title}")

    # Guardar HTML completo de la página autenticada
    html_path = "reports/portal_authenticated.html"
    import os
    os.makedirs("reports", exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"\n7. HTML guardado en: {html_path}")

    # Imprimir texto visible de la página
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"\n8. Texto visible en el portal autenticado:\n{'='*60}")
    print(body_text[:3000])
    print("="*60)

    # Intentar encontrar elementos de menú/navegación
    print("\n9. Buscando elementos de navegación...")

    # Buscar nav elements
    navs = driver.find_elements(By.TAG_NAME, "nav")
    print(f"   <nav> encontrados: {len(navs)}")
    for i, nav in enumerate(navs):
        cls = nav.get_attribute("class")
        id_ = nav.get_attribute("id")
        txt = nav.text[:100] if nav.text else "(sin texto)"
        print(f"   nav[{i}]: class='{cls}' id='{id_}' text='{txt}'")

    # Buscar sidebar
    sidebars = driver.find_elements(By.CSS_SELECTOR, "[class*='sidebar'], [class*='menu'], [class*='nav']")
    print(f"\n   Elementos con 'sidebar/menu/nav' en class: {len(sidebars)}")
    for i, el in enumerate(sidebars[:10]):
        tag = el.tag_name
        cls = el.get_attribute("class")
        id_ = el.get_attribute("id")
        txt = el.text[:80] if el.text else "(sin texto)"
        print(f"   [{i}] <{tag}> class='{cls}' id='{id_}' text='{txt}'")

    # Buscar links con href que contengan módulos conocidos
    print("\n   Buscando links de módulos (factura, nota, ppd, complemento, adenda):")
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href") or ""
        txt = link.text.strip()
        if any(kw in href.lower() or kw in txt.lower()
               for kw in ["factura", "nota", "ppd", "complemento", "adenda", "emision", "pago"]):
            cls = link.get_attribute("class")
            print(f"   <a href='{href}' class='{cls}'>{txt}</a>")

    # Buscar botones/items de menú
    print("\n   Buscando li/button con texto de módulos:")
    items = driver.find_elements(By.CSS_SELECTOR, "li, button, mat-list-item, .menu-item")
    for item in items:
        txt = item.text.strip()
        if any(kw in txt.lower()
               for kw in ["factura", "nota", "ppd", "complemento", "adenda", "pago"]):
            tag = item.tag_name
            cls = item.get_attribute("class")
            id_ = item.get_attribute("id")
            print(f"   <{tag}> class='{cls}' id='{id_}' text='{txt[:80]}'")

    print("\nInspección completada. Revisa reports/portal_authenticated.html para más detalles.")
    input("\nPresiona Enter para cerrar el navegador...")

finally:
    driver.quit()
    print("Driver cerrado.")
