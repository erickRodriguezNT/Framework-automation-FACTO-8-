# Mapa de Flujos — Auto FACTO 8

## Convención

Cada flow recibe `(driver, execution_context)` en el constructor y `test_data: dict` en `run()`.
Devuelve `{"estado": "exitoso|fallido", "error": None|str, datos...}`.

---

## Flujo: Login

```
LoginFlow.run(usuario, password)
  1. Navegar a FACTO_URL
  2. LoginPage.fill_usuario(usuario)
  3. LoginPage.fill_password(password)
  4. LoginPage.click_ingresar()
  5. HomePage.is_logged_in() → assert
  → context.set_dato("autenticado", True)
```

---

## Flujo: Factura (Ingreso / PUE)

```
FacturaFlow.run(test_data)
  1. NavigationFlow → "factura"
  2. FacturaPage.fill_receptor(rfc, nombre)
  3. FacturaPage.select_uso_cfdi(uso_cfdi)
  4. FacturaPage.select_metodo_pago("PUE")
  5. FacturaPage.select_forma_pago(forma_pago)
  6. FacturaConceptosPage.agregar_concepto(concepto)
  7. FacturaImpuestosPage.confirmar_impuestos()
  8. FacturaTimbradoFlow → captura uuid_cfdi
  9. FacturaDescargaFlow → descarga pdf, xml
  → context.set_dato("uuid_cfdi", uuid)
  → context.archivos_generados["xml"] = path_xml
  → context.archivos_generados["pdf"] = path_pdf
```

---

## Flujo: Factura PPD

```
PPDFlow.run(test_data)
  1. NavigationFlow → "ppd"
  2. PPDPage.fill_receptor(rfc, nombre)
  3. PPDPage.select_metodo_pago("PPD")
  4. PPDPage.fill_condiciones_pago(condiciones)
  5. PPDPage.agregar_concepto(concepto)
  6. PPDResultadoPage.is_timbrado() → assert
  7. PPDResultadoPage.get_uuid() → uuid_cfdi_ppd
  → context.set_dato("uuid_cfdi_ppd", uuid)
```

---

## Flujo: Complemento de Pago

**Pre-requisito**: `uuid_cfdi_ppd` en context.

```
ComplementoPagoFlow.run(test_data)
  [DependencyResolver verifica uuid_cfdi_ppd]
  1. NavigationFlow → "complemento_pago"
  2. ComplementoPagoPage.fill_fecha_pago(fecha)
  3. ComplementoPagoPage.select_forma_pago(forma)
  4. ComplementoPagoPage.fill_monto(monto)
  5. ComplementoPagoRelacionPPDFlow → relaciona documentos
  6. ComplementoPagoResultadoPage.is_timbrado() → assert
  → context.set_dato("uuid_complemento_pago", uuid)
```

---

## Flujo: Nota de Crédito

**Pre-requisito**: `uuid_factura_relacionada` en context.

```
NotaCreditoFlow.run(test_data)
  [DependencyResolver verifica uuid_factura_relacionada]
  1. NavigationFlow → "nota_credito"
  2. NotaCreditoRelacionFlow → establece uuid_relacionado
  3. NotaCreditoPage.fill_datos_receptor(...)
  4. NotaCreditoResultadoPage.is_timbrado() → assert
  → context.set_dato("uuid_nota_credito", uuid)
```

---

## Flujo: Adenda

**Pre-requisito**: `uuid_cfdi_base` en context (o en test_data).

```
AdendaFlow.run(test_data)
  [DependencyResolver verifica uuid_cfdi_base]
  1. NavigationFlow → "adenda"
  2. AdendaPage.fill_uuid_base(uuid_cfdi_base)
  3. AdendaPage.fill_tipo(tipo_adenda)
  4. AdendaPage.fill_referencia_oc(ref_oc)   # opcional
  5. AdendaPage.click_guardar()
  6. AdendaResultadoPage.is_adenda_procesada() → assert
  → context.set_dato("uuid_adenda", id_adenda)
```

---

## Flujos de Soporte

| Flow                    | Descripción                                             |
|-------------------------|---------------------------------------------------------|
| `NavigationFlow`        | Navega por el menú + espera a que cargue el loader      |
| `DownloadFlow`          | Click en botón descarga + espera al archivo en disco    |
| `ValidationFlow`        | Valida UUID CFDI (formato SAT) + existencia de archivos |
| `PPDValidacionFlow`     | Verifica estado_pago del PPD                            |
| `AdendaValidacionFlow`  | Verifica adenda procesada en ResultadoPage              |
| `ComplementoPagoValidacionFlow` | Verifica UUID CP                               |
