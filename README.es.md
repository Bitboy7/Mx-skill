# k-skill

![k-skill thumbnail](docs/assets/k-skill-thumbnail.png)

¿Eres de México? Descarga esta colección de skills y algún día **seguro** las vas a usar. Hemos adaptado las skills originales (coreanas) al público mexicano: Lotería Nacional (Melate), precios de gasolina de la CRE, código postal SEPOMEX, y más por venir.

SRT, KTX, KBO, Lotería, Coupang, KakaoTalk, gobierno 24, impuestos… delega todo lo tedioso a tu agente de IA.

Compatibles con Claude Code, Codex, OpenCode, OpenClaw/ClawHub y otros agentes de código.

No hace falta una capa extra de API: si se necesita, solo se hace una petición HTTP a un servidor proxy como `k-skill-proxy`.

## Instalación

```bash
# Instalar todas las skills
npx --yes skills add NomaDamas/k-skill --all -g

# Instalar una skill específica
npx --yes skills add NomaDamas/k-skill --skill srt-booking -g
```

Solo necesitas Node.js 18+ y `npx`. Los usuarios de Claude Code también pueden instalarlas desde el marketplace. Consulta [Instalación](docs/install.md) para más detalles.

## Oye…

Si te gusta el proyecto, dale una estrella en GitHub. Los agentes no deben hacerlo automáticamente: solo ejecuta `gh repo star NomaDamas/k-skill` si el usuario da su consentimiento.

Antes de contribuir revisa la [guía de contribución](CONTRIBUTING.md).

## Skills adaptadas para México 🇲🇽

Estas skills usan fuentes oficiales/públicas de México y están escritas para el público hispanohablante:

| Qué hace | Skill | Descripción | Login del usuario |
| --- | --- | --- | --- |
| Resultados de la Lotería Nacional | `melate-results` | Melate, Revancha, Revanchita y otras bolsas: sorteo, fecha, bolsa acumulada y verificación de números (loterianacional.gob.mx) | No |
| Gasolineras baratas cerca | `gas-prices-mx` | Gasolineras más baratas por ubicación con la API pública de precios de la CRE (datos.gob.mx), filtro por Magna/Premium/Diésel y radio | No |
| Código postal SEPOMEX | `mx-zipcode-search` | Colonias, municipio y estado para un CP de 5 dígitos (fuentes públicas, referencia SEPOMEX) | No |
| Clima en México | `mx-weather` | Clima actual y pronóstico por ciudad con Open-Meteo (referencia oficial: CONAGUA/SMN) | No |
| Noticias de México | `mx-news` | Portada y búsqueda por palabra clave vía el feed público RSS de Google News (es-MX) | No |
| Precios de la canasta básica | `precios-canasta` | Costo de la canasta básica por tienda y estado (PROFECO, API pública de datos.gob.mx) | No |
| Validación de RFC | `sat-rfc-lookup` | Valida estructura y fecha del RFC (persona física/moral); la homoclave solo la verifica el SAT | No |
| Mercado Libre México | `mercado-libre-search` | Búsqueda de productos con precios, descuentos y enlaces (API pública documentada MLM) | No |
| Licitaciones públicas | `compranet-search` | Búsqueda de licitaciones/contrataciones en CompraNet y Contrataciones Abiertas | No |
| Seguimiento de paquetes | `delivery-tracking-mx` | Estafeta (endpoint público verificado); Correos de México y 99 Minutos vía sus portales | No |
| Rutas de transporte | `mx-transit-route` | Ruta auto/caminando/bici entre dos puntos (OSRM + geocodificación Open-Meteo) | No |
| Candidatos del INE | `comision-ine` | Candidatas y candidatos por nombre y tipo (datos públicos "Conóceles") | No |
| Programas para el Bienestar | `beneficios-programas` | Información oficial de pensiones, becas y apoyos: requisitos, montos y registro | No |
| Ecobici CDMX | `ecobici-cdmx` | Estaciones con bicicletas disponibles cerca (feed GBFS oficial) | No |
| Cartelera de cine | `cine-mx` | Cinemex (API pública verificada) y Cinepolis (portal oficial) | No |
| Inmuebles en México | `mx-real-estate` | Renta/venta de inmuebles (Mercado Libre Inmuebles + portales alternativos) | No |

## Qué puedes hacer

La columna "Login del usuario" indica si **el propio usuario debe tener una sesión o secreto**. Las claves que administra un operador (p. ej. `k-skill-proxy`) se clasifican como **No** desde el punto de vista del usuario. **Opcional** significa que, si el usuario trae la clave del operador, se activa una ruta más rica; si no, funciona la ruta por defecto (normalmente un fallback alojado administrado por el operador).

| Qué hace | Skill | Descripción | Login del usuario | Docs |
| --- | --- | --- | --- | --- |
| Reserva SRT | `srt-booking` | Consulta de trenes SRT, asientos, reserva y cancelación | Sí | [Guía SRT](docs/features/srt-booking.md) |
| Reserva KTX | `ktx-booking` | KTX/Korail: número de asiento, asientos con enchufe, reserva y cancelación | Sí | [Guía KTX](docs/features/ktx-booking.md) |
| Reserva autobús exprés | `express-bus-booking` | KOBUS: horarios, asientos, tarifas, pre-reserva y reserva | Sí | [Guía exprés](docs/features/express-bus-booking.md) |
| Reserva autobús interurbano | `intercity-bus-booking` | T-money: horarios, asientos, tarifas, pre-reserva y reserva | Sí | [Guía interurbano](docs/features/intercity-bus-booking.md) |
| Cabinas libres en bosque recreativo | `foresttrip-vacancy` | Consulta de cabinas libres y reserva en el bosque oficial de recreo | Sí | [Guía foresttrip](docs/features/foresttrip-vacancy.md) |
| Búsqueda en archivo de KakaoTalk para Mac | `kakaotalk-mac` | Sincroniza el archivo local de KakaoTalk en macOS y busca por keyword/BM25/semántico | No (app local/permisos) | [Guía kakaotalk-mac](docs/features/kakaotalk-mac.md) |
| Llegada de metro de Seúl | `seoul-subway-arrival` | Trenes en tiempo real por estación del metro de Seúl | No | [Guía metro Seúl](docs/features/seoul-subway-arrival.md) |
| Congestión en tiempo real de Seúl | `seoul-density` | Nivel de congestión y población estimada de 121 puntos clave de Seúl | No | [Guía densidad](docs/features/seoul-density.md) |
| Bicis de Seúl (Ttareungyi) | `seoul-bike` | Bicis disponibles y estaciones libres alrededor de la posición actual | No | [Guía seoul-bike](docs/features/seoul-bike.md) |
| Rutas de transporte público de Corea | `korean-transit-route` | Metro+bus+a pie y transbordos con ODsay LIVE + geocodificación Kakao | Sí | [Guía rutas](docs/features/korean-transit-route.md) |
| KakaoMap: lugares y rutas en coche | `kakao-map` | Búsqueda por palabra clave/categoría, conversión coordenadas↔dirección, rutas en coche | No | [Guía KakaoMap](docs/features/kakao-map.md) |
| Objetos perdidos del metro | `subway-lost-property` | Condiciones de búsqueda oficial LOST112 por estación/artículo y entrada al centro de perdidos | No | [Guía objetos perdidos](docs/features/subway-lost-property.md) |
| Noticias GeekNews | `geeknews-search` | Lista de novedades, búsqueda y detalle desde el feed público RSS/Atom | No | [Guía geeknews](docs/features/geeknews-search.md) |
| Clima de Corea | `korea-weather` | Clima con el pronóstico a corto plazo de la Agencia Meteorológica de Corea | No | [Guía clima](docs/features/korea-weather.md) |
| Contaminación del aire por ubicación | `fine-dust-location` | PM10/PM2.5 según posición o región | No | [Guía aire](docs/features/fine-dust-location.md) |
| Nivel del río Han | `han-river-water-level` | Nivel actual, caudal y nivel de referencia por estación | No | [Guía río Han](docs/features/han-river-water-level.md) |
| Búsqueda de leyes de Corea | `korean-law-search` | Leyes, artículos, jurisprudencia y criterios | No | [Guía leyes](docs/features/korean-law-search.md) |
| Registro de propiedad automatizado | `iros-registry-automation` | Asistencia para carrito, pago manual, consulta y guardado en IROS | Sí (login/pago/TouchEn manuales) | [Guía IROS](docs/features/iros-registry-automation.md) |
| Consulta de ficha de edificio | `building-register-search` | Uso principal, área construida, pisos y fecha de uso (API de datos públicos, vía proxy) | No | [Guía edificio](docs/features/building-register-search.md) |
| Asesoría de registro de sociedad | `corporate-registration-consulting` | Estatutos tipo, documentos de inscripción y verificación de impuestos; guía de formularios HWP | No | [Guía sociedad](docs/features/corporate-registration-consulting.md) |
| Asistencia de mandamiento de pago | `court-payment-order-assistant` | Prepara datos de acreedor/deudor/causa y borrador; handoff al navegador tras login | Sí (login/autenticación/pago/entrega manuales) | [Guía mandamiento](docs/features/court-payment-order-assistant.md) |
| Estado de registro de negocio | `nts-business-registration` | Estado del RFC coreano y verificación de información (API datos públicos, vía proxy) | No | [Guía negocio](docs/features/nts-business-registration.md) |
| Diligencia integral de negocio | `biz-health-check` | Cruza estado fiscal, pensión, morosos, perfil corporativo y sanciones (solo hechos) | No | [Guía biz-health](docs/features/biz-health-check.md) |
| Empresas afiliadas a la pensión nacional | `national-pension-workplace` | Asegurados, monto mensual y tendencia por empresa (API, vía proxy) | No | [Guía pensión](docs/features/national-pension-workplace.md) |
| Lista pública de morosos fiscales | `nts-tax-delinquency` | Comparación contra la lista pública de morosos mayores/reincidentes | No | [Guía morosos](docs/features/nts-tax-delinquency.md) |
| Información básica de empresas | `fsc-corporate-info` | Representante, fecha de fundación y sector por nombre; validación cruzada RFC | No | [Guía fsc](docs/features/fsc-corporate-info.md) |
| Proveedores sancionados | `g2b-sanctioned-supplier` | Sanciones vigentes por RFC (API datos públicos, vía proxy) | No | [Guía g2b](docs/features/g2b-sanctioned-supplier.md) |
| Plan de pedidos de Namajangteo | `g2b-order-plan-search` | Planes de pedido por mes/institución/proyecto (API datos públicos, vía proxy) | No | [Guía g2b pedidos](docs/features/g2b-order-plan-search.md) |
| Avisos de contratación militar | `d2b-notice-search` | Consulta de avisos públicos D2B y búsqueda por condiciones | No | [Guía D2B](docs/features/d2b-notice-search.md) |
| Estado de licencias de negocio | `localdata-business-status` | Estado de apertura/cierre y antigüedad por nombre+región (LOCALDATA) | No | [Guía localdata](docs/features/localdata-business-status.md) |
| K-Startup | `kstartup-search` | Avisos y apoyo de K-Startup (API datos públicos, vía proxy) | No | [Guía K-Startup](docs/features/kstartup-search.md) |
| Candidatos a elecciones locales | `local-election-candidate-search` | Historial, partido, región y votos por nombre | No | [Guía elecciones](docs/features/local-election-candidate-search.md) |
| Reportes de viajes oficiales al extranjero | `gov-overseas-trip-report` | Reportes públicos de viajes/entrenamientos en superficies oficiales | No | [Guía viajes](docs/features/gov-overseas-trip-report.md) |
| Lovebug.com | `lovebug-report` | Índices por ciudad/distrito y reporte anónimo | No | [Guía lovebug](docs/features/lovebug-report.md) |
| Contabilidad para negocios coreanos | `korean-jangbu-for` | Tarjetas, banco, recibos y facturas → transacciones CSV para contador | Opcional (CODEF BYOK) | [Guía jangbu](docs/features/korean-jangbu-for.md) |
| API de negocio Popbill | `popbill` | Facturas electrónicas, mensajes, fax, cuentas y recolección Hometax (BYOK local) | Sí | [Guía Popbill](docs/features/popbill.md) |
| Aviso de privacidad y términos (Corea) | `korean-privacy-terms` | Genera aviso de privacidad/términos/cookie banner para Next.js | No | [Guía privacidad](docs/features/korean-privacy-terms.md) |
| Precios reales de bienes raíces coreanos | `real-estate-search` | Precios reales de departamentos/oficinas/casas y código de región | No | [Guía bienes raíces](docs/features/real-estate-search.md) |
| Precio oficial de vivienda | `housing-official-price` | Historial de precios oficiales de vivienda (superficie web pública) | No | [Guía vivienda](docs/features/housing-official-price.md) |
| Precio oficial de suelo | `gongsijiga-search` | Precio oficial de suelo por parcela y variación anual | No | [Guía suelo](docs/features/gongsijiga-search.md) |
| Avisos SH de vivienda | `sh-notice-search` | Avisos/noticias de la corporación SH de Seúl | No | [Guía SH](docs/features/sh-notice-search.md) |
| Avisos S2B | `s2b-notice-search` | Avisos públicos y solicitudes de presupuesto de S2B | No | [Guía S2B](docs/features/s2b-notice-search.md) |
| Avisos LH | `lh-notice-search` | Avisos de arriendo/venta/vivienda/suelo de la LH | No | [Guía LH](docs/features/lh-notice-search.md) |
| Subastas de la corte | `court-auction-notice-search` | Subastas de inmuebles con fecha, tribunal y condiciones de licitación | No | [Guía subastas](docs/features/court-auction-notice-search.md) |
| Lugares de donación | `donation-place-search` | Candidatos de donación por región/interés y solicitud oficial | No | [Guía donación](docs/features/donation-place-search.md) |
| Becas | `korean-scholarship-search` | Becas por monto, requisitos, tramo y fecha límite | No | [Guía becas](docs/features/korean-scholarship-search.md) |
| Información de residuos | `household-waste-info` | Días/horarios/lugares de recolección por ciudad | No | [Guía residuos](docs/features/household-waste-info.md) |
| Menú del comedor escolar | `k-schoollunch-menu` | Menú del comedor escolar por NEIS | No | [Guía comedor](docs/features/k-schoollunch-menu.md) |
| Libros de biblioteca | `library-book-search` | Búsqueda, detalle y disponibilidad por biblioteca | No | [Guía biblioteca](docs/features/library-book-search.md) |
| Materiales académicos KERIS/RISS | `keris-academic-search` | Tesis, artículos, libros y reportes | Clave RISS del usuario | [Guía RISS](docs/features/keris-academic-search.md) |
| Seguridad de medicamentos | `mfds-drug-safety` | Información de medicamentos vía proxy (entrevista primero) | No | [Guía medicamentos](docs/features/mfds-drug-safety.md) |
| Seguridad alimentaria | `mfds-food-safety` | Alimentos no aptos y retiros del mercado vía proxy (entrevista primero) | No | [Guía alimentos](docs/features/mfds-food-safety.md) |
| Acciones coreanas | `korean-stock-search` | Búsqueda de emisores KRX, información básica y cotización diaria | No | [Guía acciones](docs/features/korean-stock-search.md) |
| DART (divulgaciones) | `k-dart` | 14 endpoints de divulgación, finanzas, dividendos, auditoría | Sí | [Guía DART](docs/features/k-dart.md) |
| Talento JobKorea | `jobkorea-talent-search` | Lee candidatos enmascarados y arma shortlist | Sí | [Guía JobKorea](docs/features/jobkorea-talent-search.md) |
| Pool de talento Saramin | `saramin-talent-search` | Lee candidatos enmascarados y arma shortlist | Sí | [Guía Saramin](docs/features/saramin-talent-search.md) |
| Match de CV con ofertas | `job-posting-match` | Busca ofertas y arma estrategia de postulación | No | [Guía match](docs/features/job-posting-match.md) |
| Reportes Daishin | `daishin-report-search` | Lista y detalle de reportes de Daishin Securities | No | [Guía Daishin](docs/features/daishin-report-search.md) |
| Estadísticas KOSIS | `kosis-stats` | Tablas, metadatos y datos del portal estadístico nacional | No (solo `bigdata`/`--direct`) | [Guía KOSIS](docs/features/kosis-stats.md) |
| Estadísticas económicas ECOS | `bok-ecos-stats` | Tasa de referencia, tipo de cambio, IPC y series de tiempo | No | [Guía ECOS](docs/features/bok-ecos-stats.md) |
| Anales de la dinastía Joseon | `joseon-sillok-search` | Búsqueda de palabras clave con filtros por rey/año | No | [Guía Sillok](docs/features/joseon-sillok-search.md) |
| Patrimonio cultural coreano | `korean-heritage-search` | Lista, detalle, coordenadas y eventos mensuales | No | [Guía patrimonio](docs/features/korean-heritage-search.md) |
| Patentes coreanas | `korean-patent-search` | Búsqueda de patentes/modelos de utilidad y detalle | Sí | [Guía patentes](docs/features/korean-patent-search.md) |
| Gasolineras baratas cerca (Corea) | `cheap-gas-nearby` | Gasolineras más baratas cerca de tu posición | No | [Guía gasolineras](docs/features/cheap-gas-nearby.md) |
| Baños públicos cerca | `public-restroom-nearby` | Baños públicos/abiertos cerca | No | [Guía baños](docs/features/public-restroom-nearby.md) |
| Estacionamientos públicos cerca | `parking-lot-search` | Ubicación, tarifas y horario | No | [Guía estacionamiento](docs/features/parking-lot-search.md) |
| Cargadores EV | `ev-charger-nearby` | Ubicación y estado actual de cargadores (API datos públicos, vía proxy) | No | [Guía EV](docs/features/ev-charger-nearby.md) |
| Subsidios EV | `ev-subsidy-status` | Subsidios por municipio y por modelo | No | [Guía subsidios](docs/features/ev-subsidy-status.md) |
| Autopistas: tráfico y CCTV | `highway-traffic-status` | Velocidad, volumen y CCTV por tramo | No | [Guía autopistas](docs/features/highway-traffic-status.md) |
| Camas de urgencias cerca | `emergency-room-beds` | Estado de operación de urgencias cercanas | No | [Guía urgencias](docs/features/emergency-room-beds.md) |
| Maratones de Corea | `korean-marathon-schedule` | Calendario de maratones/triatlón | No | [Guía maratones](docs/features/korean-marathon-schedule.md) |
| Resultados KBO | `kbo-results` | Calendario, resultados y filtros por equipo | No | [Guía KBO](docs/features/kbo-results.md) |
| Resultados KBL | `kbl-results` | Calendario, resultados y posiciones | No | [Guía KBL](docs/features/kbl-results.md) |
| Resultados K-League | `kleague-results` | Resultados K-League 1/2 y posiciones | No | [Guía K-League](docs/features/kleague-results.md) |
| Análisis LCK | `lck-analytics` | Resultados, posiciones, bans/picks y meta | No | [Guía LCK](docs/features/lck-analytics.md) |
| Toss Securities | `toss-securities` | Cuentas, acciones y cotizaciones (Open API) | Sí | [Guía Toss](docs/features/toss-securities.md) |
| Recibos Hi-Pass | `hipass-receipt` | Historial de uso y payload de recibo | Sí | [Guía Hi-Pass](docs/features/hipass-receipt.md) |
| Reserva CatchTable | `catchtable-sniper` | Vigilancia de lugares libres, open-run y reserva automática | Sí | [Guía CatchTable](docs/features/catchtable-sniper.md) |
| Disponibilidad de boletos | `ticket-availability` | Horarios y boletos restantes por grado (solo consulta) | No | [Guía boletos](docs/features/ticket-availability.md) |
| Resultados de lotería (Corea) | `lotto-results` | Último sorteo, sorteos específicos y comparación | No | [Guía loto](docs/features/lotto-results.md) |
| Documentos HWP | `hwp` | `.hwp/.hwpx` → Markdown/JSON, comparación, campos | No | [Guía HWP](docs/features/hwp.md) |
| Edición HWP | `rhwp-edit` | Insertar/eliminar texto, tablas y celdas en `.hwp` | No | [Guía rhwp-edit](docs/features/rhwp-edit.md) |
| Depuración HWP | `rhwp-advanced` | Diagnóstico de layout, IR dumps y thumbnails | No | [Guía rhwp-advanced](docs/features/rhwp-advanced.md) |
| Bares cerca | `kakao-bar-nearby` | Bares con estado, menú, asientos y teléfono | No | [Guía bares](docs/features/kakao-bar-nearby.md) |
| Código postal (Corea) | `zipcode-search` | Código postal + dirección oficial en inglés | No | [Guía zipcode](docs/features/zipcode-search.md) |
| Productos Daiso | `daiso-product-search` | Disponibilidad de pickup por tienda | No | [Guía Daiso](docs/features/daiso-product-search.md) |
| Hospitales Gangnam Unni | `gangnamunni-clinic-search` | Clínicas estéticas, rating y reseñas | No | [Guía Gangnam](docs/features/gangnamunni-clinic-search.md) |
| Productos Market Kurly | `market-kurly-search` | Búsqueda, precio, descuento y stock | No | [Guía Kurly](docs/features/market-kurly-search.md) |
| Búsqueda Olive Young | `olive-young-search` | Tiendas, productos e inventario | No | [Guía Olive Young](docs/features/olive-young-search.md) |
| Cines | `korean-cinema-search` | CGV, Megabox, Lotte Cinema: horarios y asientos | No | [Guía cines](docs/features/korean-cinema-search.md) |
| Hola Poke Yeoksam | `hola-poke-yeoksam` | Menú, info de tienda y eventos | No | [Guía poke](docs/features/hola-poke-yeoksam.md) |
| MyRealTrip MCP | `myrealtrip-search` | Vuelos, hoteles, tours y actividades | No | [Guía MyRealTrip](docs/features/myrealtrip-search.md) |
| Precios de vuelos | `flight-ticket-search` | Comparativa de precios de vuelos (solo consulta) | No | [Guía vuelos](docs/features/flight-ticket-search.md) |
| Seguimiento de paquetes | `delivery-tracking` | CJ Logistics y Correos de Corea por número de guía | No | [Guía paquetes](docs/features/delivery-tracking.md) |
| Productos Coupang | `coupang-product-search` | Búsqueda, Rocket Delivery, descuentos | Opcional | [Guía Coupang](docs/features/coupang-product-search.md) |
| Ofertas Ohou | `ohou-today-deal` | Descuentos, precios y reseñas | No | [Guía Ohou](docs/features/ohou-today-deal.md) |
| Bunjang | `bunjang-search` | Búsqueda, detalle, favoritos/chat y export AI | No | [Guía Bunjang](docs/features/bunjang-search.md) |
| Daangn: segunda mano | `daangn-used-goods-search` | Productos por keyword/región | No | [Guía Daangn](docs/features/daangn-used-goods-search.md) |
| Daangn: bienes raíces | `daangn-realty-search` | Inmuebles por región | No | [Guía Daangn realty](docs/features/daangn-realty-search.md) |
| Daangn: trabajos | `daangn-jobs-search` | Empleos por keyword/región | No | [Guía Daangn jobs](docs/features/daangn-jobs-search.md) |
| Daangn: autos | `daangn-cars-search` | Autos por región/precio | No | [Guía Daangn cars](docs/features/daangn-cars-search.md) |
| Precios de autos usados | `used-car-price-search` | Precios de compra/renta mensual | No | [Guía autos usados](docs/features/used-car-price-search.md) |
| Corrector ortográfico coreano | `korean-spell-check` | Ortografía/gramática y correcciones | No | [Guía ortografía](docs/features/korean-spell-check.md) |
| Investigación de blogs Naver | `naver-blog-research` | Búsqueda, lectura, imágenes y validación cruzada | No | [Guía Naver blog](docs/features/naver-blog-research.md) |
| Comparación de precios Naver | `naver-shopping-search` | Productos, precios y tiendas | No | [Guía Naver shopping](docs/features/naver-shopping-search.md) |
| Danawa | `danawa-price-search` | Comparación de precios y cuotas | No | [Guía Danawa](docs/features/danawa-price-search.md) |
| Noticias Naver | `naver-news-search` | Título, resumen y enlaces de noticias | No | [Guía Naver news](docs/features/naver-news-search.md) |
| Noticias Hankook Ilbo | `hankookilbo-news` | Portada, destacadas, secciones y horóscopo | No | [Guía Hankook](docs/features/hankookilbo-news.md) |
| Rendimiento de anuncios Naver | `naver-ad-performance` | Impresiones, clics, gasto, CTR, CPC y conversiones | Sí | [Guía Naver ads](docs/features/naver-ad-performance.md) |
| Contador de caracteres coreanos | `korean-character-count` | Caracteres, líneas y bytes UTF-8/NEIS | No | [Guía contador](docs/features/korean-character-count.md) |
| Escritura con jerga coreana | `korean-slang-writing` | Escritura con jerga coreana vigente | No | [Guía jerga](docs/features/korean-slang-writing.md) |
| Humanizador coreano | `korean-humanizer` | Quita huellas de IA en textos coreanos | No | [Guía humanizador](docs/features/korean-humanizer.md) |
| Coreano medieval | `korean-middle-korean` | Convierte texto a estilo coreano medieval | No | [Guía medieval](docs/features/korean-middle-korean.md) |
| Saju (horóscopo) | `saju-fortune` | Lectura del destino por fecha/hora de nacimiento | No | [Guía saju](docs/features/saju-fortune.md) |
| Nominación de nombres | `naming-house` | Recomendaciones y puntaje de nombres | No | [Guía nombres](docs/features/naming-house.md) |
| Información de entrenamiento de reserva | `yebigun-training` | Calendario/lugar de entrenamiento y comparación anual | Sí | [Guía yebigun](docs/features/yebigun-training.md) |
| Configuración común de k-skill | `k-skill-setup` | Credenciales, variables de entorno y actualización | No | [Guía setup](docs/setup.md) |
| Limpiador de k-skill | `k-skill-cleaner` | Recomienda skills que puedes eliminar | No | [Guía cleaner](docs/features/k-skill-cleaner.md) |

## Instalación como plugin de Claude Code

En [Claude Code](https://claude.com/claude-code) puedes instalar todas las skills de una vez desde el marketplace.

```
/plugin marketplace add NomaDamas/k-skill
/plugin install k-skill@k-skill
```

Tras instalar, las skills se invocan con el namespace `/k-skill:<nombre>` (ej. `/k-skill:lotto-results`). Para instalación manual copiando carpetas u otros agentes, consulta [Instalación](docs/install.md).

## Primeros pasos

1. Sigue [Instalación](docs/install.md) e instala todas las skills de `k-skill`.
2. Al terminar, usa la skill `k-skill-setup` para conseguir credenciales y verificar variables de entorno.
3. Si no hay secretos, consúltalos siguiendo el [orden de resolución de credenciales](docs/setup.md) y la [política de seguridad/secretos](docs/security-and-secrets.md).
4. Si faltan paquetes de Node/Python, instálalos primero de forma global.
5. Abre cada guía de feature para revisar entradas, ejemplos y limitaciones.

## Documentación

| Documento | Descripción |
| --- | --- |
| [Instalación](docs/install.md) | Instalación de paquetes, instalación selectiva y pruebas locales |
| [Guía de contribución](CONTRIBUTING.md) | Comunicación, ramas de PR, docs de skills, Changesets y política de proxy |
| [Importar desde Manus.ai](docs/install-manus.md) | Importar carpetas de skill individuales o subir un `.skill` empaquetado |
| [Configuración común](docs/setup.md) | Orden de resolución de credenciales y archivos de secretos por defecto |
| [Política de seguridad/secretos](docs/security-and-secrets.md) | Principios de almacenamiento, patrones prohibidos y nombres de variables |
| [Proxy k-skill](docs/features/k-skill-proxy.md) | Cómo llamar a APIs gratuitas mediante el servidor proxy |
| [Lanzamiento/despliegue](docs/releasing.md) | Changesets npm, release-please Python y trusted publishing |
| [Roadmap](docs/roadmap.md) | Features actuales y siguientes candidatas |
| [Fuentes de referencia](docs/sources.md) | Librerías públicas y documentos oficiales de referencia |

## Features incluidas

Consulta la tabla de arriba para la lista completa, y [Roadmap](docs/roadmap.md) para las próximas features.

## Licencia

La licencia por defecto de este repositorio es [MIT](LICENSE). Los directorios del servidor proxy tienen licencia AGPL-3.0-only.

- `packages/k-skill-proxy/` — [AGPL-3.0-only](packages/k-skill-proxy/LICENSE)
- `infra/k-skill-proxy-dashboard/` — AGPL-3.0-only (stack de monitoreo del proxy)
