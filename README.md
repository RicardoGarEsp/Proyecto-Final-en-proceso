# Proyecto Final: Gestión y Análisis de Datos Relacionales en la Nube usando Global Superstore Orders 2016

## 🧾 Resumen del Proyecto

| Campo | Descripción |
|---------|-------------|
| **Pregunta analítica** | ¿Qué productos, categorías y regiones generan la mayor rentabilidad y cuáles están reduciendo las ganancias debido a descuentos elevados y altos costos de envío? |
| **Dataset** | Global Superstore Orders 2016. Contiene información de pedidos, clientes, productos, ventas, descuentos, beneficios, costos de envío, mercados y regiones geográficas. |
| **Fuente** | https://www.kaggle.com/datasets/jaredrosas/global-superstore-orders-2016-es-esp |
| **Modelo** | Modelo dimensional tipo Star Schema con una tabla de hechos de ventas y dimensiones de Cliente, Producto, Tiempo y Geografía. |
| **Infraestructura** | PostgreSQL para almacenamiento y consultas, con Streamlit para la construcción de dashboards e indicadores de negocio. |
| **ETL** | **Extract:** Extracción de los datos desde el archivo Excel *Global Superstore Orders 2016_es-ES.xlsx*.<br><br>**Transform:** Limpieza de fechas, eliminación de duplicados, construcción de dimensiones, generación de claves sustitutas, creación de la tabla de hechos y validación del modelo estrella.<br><br>**Load:** Exportación del modelo a Excel y carga del esquema **ecomerce_dwh** en PostgreSQL (AWS Aurora). |
| **SQL Avanzado** | Implementación de consultas analíticas utilizando **CTE (Common Table Expressions)**, **funciones de ventana (Window Functions)**, **RANK()**, **LAG()**, **COUNT() FILTER** y **PERCENTILE_CONT()** para realizar rankings, promedios móviles, agregaciones condicionales, comparaciones temporales y análisis estadísticos sobre el modelo estrella. |
| **Dashboard** | Dashboard interactivo basado en las querys propuestas |

## 📁 Estructura del repositorio
```
Proyecto-Final-en-proceso/
├── README.md                           ← este archivo
├── DATOS/
    ├── etl+querys.md                   ← proceso etl y querys de SQL en entorno de python probando la conexión con Aurora
    ├── DASHBOARD/                       
        ├── dashboard.py                ← dashboard que cargará Streamlit
        ├── requirements.txt            ← librerías que requiere Streamlit
        └── query.xlsx                  ← datos fijos que ya no dependen de la conexión con Aurora

```

## 🎯 Objetivo de Negocio 

Se seleccionó el dataset **Global Superstore Orders 2016** debido a que representa un escenario empresarial realista donde se integran procesos de ventas, logística, clientes y productos. Este tipo de datos permite aplicar técnicas de Business Intelligence y análisis de datos para generar información valiosa para la toma de decisiones, identificando oportunidades de mejora en rentabilidad, segmentación de clientes y optimización de costos de envío.

La principal ventaja de este dataset es que contiene múltiples dimensiones de análisis (tiempo, geografía, clientes y productos), lo que permite construir modelos analíticos completos, consultas SQL avanzadas y dashboards ejecutivos similares a los utilizados en entornos empresariales reales.

Mediante análisis del dataset podemos reponder varias preguntas como lo pueden ser:
- ¿Qué productos generan la mayor rentabilidad?
- ¿Qué categorías tienen mayores ventas pero menores márgenes?
- ¿Cómo impactan los descuentos en el beneficio final?
- ¿Qué regiones presentan mejor desempeño comercial?
- ¿Qué modos de envío generan mayores costos logísticos?

## 📊 Descripción del Dataset inicial

| Campo | Descripción |
|--------|-------------|
| ID de fila | Identificador único del registro |
| ID de pedido | Identificador único de cada pedido |
| Fecha de pedido | Fecha en que se realizó la compra |
| Fecha de envío | Fecha en que se despachó el pedido |
| Modo de envío | Tipo de envío seleccionado por el cliente |
| ID de cliente | Identificador único del cliente |
| Nombre de cliente | Nombre del cliente |
| Segmento | Segmento comercial del cliente (Consumidor, Corporativo, etc.) |
| Código postal | Código postal de la ubicación del cliente |
| Ciudad | Ciudad donde se realizó la venta |
| Estado | Estado o provincia correspondiente |
| País | País donde se realizó la venta |
| Región | Región comercial asociada |
| Mercado | Mercado geográfico de operación |
| ID de producto | Identificador único del producto |
| Categoría | Categoría principal del producto |
| Subcategoría | Clasificación específica dentro de la categoría |
| Nombre de producto | Nombre comercial del producto |
| Ventas | Importe total de la venta |
| Cantidad | Número de unidades vendidas |
| Descuento | Descuento aplicado a la venta |
| Beneficio | Ganancia obtenida por la venta |
| Costo de envío | Costo asociado al transporte del pedido |
| Prioridad de pedido | Nivel de prioridad asignado al pedido |
| Persona | Persona encargada de la región |
 ---
 
## ⭐ Modelo Estrella

```mermaid
erDiagram

    FACT_VENTAS {
        int id_fila PK
        string id_pedido

        string id_cliente FK
        string id_producto FK
        int id_geografia FK
        int id_tiempo FK
        int id_envio FK
        int id_persona FK

        decimal ventas
        int cantidad
        decimal descuento
        decimal beneficio
        decimal costo_envio
    }

    DIM_CLIENTE {
        string id_cliente PK
        string nombre_cliente
        string segmento
    }

    DIM_PRODUCTO {
        string id_producto PK
        string categoria
        string subcategoria
        string nombre_producto
    }

    DIM_GEOGRAFIA {
        int id_geografia PK
        string codigo_postal
        string ciudad
        string estado
        string pais
        string region
        string mercado
    }

    DIM_TIEMPO {
        int id_tiempo PK
        date fecha_pedido
        int dia
        int mes
        int trimestre
        int anio
    }

    DIM_ENVIO {
        int id_envio PK
        date fecha_envio
        string modo_envio
        string prioridad_pedido
    }

    DIM_PERSONA {
        int id_persona PK
        string persona
        string region
    }

    DIM_CLIENTE ||--o{ FACT_VENTAS : cliente
    DIM_PRODUCTO ||--o{ FACT_VENTAS : producto
    DIM_GEOGRAFIA ||--o{ FACT_VENTAS : geografia
    DIM_TIEMPO ||--o{ FACT_VENTAS : tiempo
    DIM_ENVIO ||--o{ FACT_VENTAS : envio
    DIM_PERSONA ||--o{ FACT_VENTAS : responsable
```

## 🧩 Diseño del Modelo Dimensional

Para este proyecto se implementó un modelo dimensional tipo **Esquema de Estrella** debido a que es uno de los enfoques más utilizados en entornos de Business Intelligence y Data Warehousing. Este modelo facilita el análisis de grandes volúmenes de datos mediante la separación de los indicadores de negocio y los atributos descriptivos.

La tabla central **Fact_Ventas** almacena las métricas cuantitativas que representan los eventos de negocio, como ventas, cantidad de productos vendidos, descuentos, beneficios y costos de envío. Estas métricas son las que posteriormente se analizarán mediante consultas SQL y visualizaciones.

Por otro lado, las tablas de dimensión contienen información descriptiva que permite segmentar y analizar los datos desde diferentes perspectivas:

- **Dim_Cliente:** permite analizar el comportamiento de compra por cliente y segmento.
- **Dim_Producto:** facilita el estudio de categorías, subcategorías y productos específicos.
- **Dim_Geografia:** permite evaluar el desempeño comercial por ciudad, estado, país, región y mercado.
- **Dim_Tiempo:** posibilita realizar análisis temporales, tendencias y comparaciones históricas.
- **Dim_Envio:** ayuda a evaluar la eficiencia logística y el impacto de los métodos de envío en la rentabilidad.
- **Dim_Persona:** permite analizar el desempeño comercial por responsable regional.

### 📋 Criterios de Diseño

La separación de las dimensiones se realizó siguiendo los siguientes criterios:

1. **Agrupación temática:** cada dimensión representa una entidad de negocio claramente identificable (cliente, producto, ubicación, tiempo, envío y responsable).
2. **Reducción de redundancia:** los atributos descriptivos se almacenan una sola vez y son reutilizados mediante claves foráneas.
3. **Facilidad de análisis:** el modelo permite responder preguntas de negocio desde múltiples perspectivas sin realizar consultas complejas sobre una única tabla transaccional.
4. **Escalabilidad:** facilita la incorporación futura de nuevas métricas o dimensiones sin afectar significativamente el modelo existente.


## ⛃ SQL Avanzado 

### 1. CTE + Ranking simple, ¿Qué productos generan la mayor rentabilidad?
```
WITH rentabilidad_producto AS (

    SELECT
        dp."Nombre de producto" AS producto,
        SUM(fv."Beneficio") AS beneficio_total

    FROM ecomerce_dwh.fact_ventas fv
    JOIN ecomerce_dwh.dim_producto dp
        ON fv."ID de producto" = dp."ID de producto"

    GROUP BY dp."Nombre de producto"

)

SELECT
    producto,
    beneficio_total,
    RANK() OVER(ORDER BY beneficio_total DESC) AS ranking

FROM rentabilidad_producto

ORDER BY ranking
LIMIT 10;
```

### 2. Window Function, ¿Qué categorías tienen mayores ventas pero menores márgenes?
```
SELECT

    dp."Categoría",

    SUM(fv."Ventas") AS ventas_totales,

    SUM(fv."Beneficio") AS beneficio_total,

    ROUND(
        (
            SUM(fv."Beneficio") /
            NULLIF(SUM(fv."Ventas"),0)
        )::numeric,
        4
    ) AS margen,

    AVG(SUM(fv."Ventas")) OVER() AS promedio_ventas

FROM ecomerce_dwh.fact_ventas fv

JOIN ecomerce_dwh.dim_producto dp
ON fv."ID de producto" = dp."ID de producto"

GROUP BY dp."Categoría"

ORDER BY ventas_totales DESC;
```

### 3. COUNT FILTER, ¿Cómo impactan los descuentos en el beneficio final?
```
SELECT

    COUNT(*) FILTER (
        WHERE "Descuento" = 0
    ) AS pedidos_sin_descuento,

    COUNT(*) FILTER (
        WHERE "Descuento" > 0
    ) AS pedidos_con_descuento,

    AVG("Beneficio") FILTER (
        WHERE "Descuento" = 0
    ) AS beneficio_promedio_sin_descuento,

    AVG("Beneficio") FILTER (
        WHERE "Descuento" > 0
    ) AS beneficio_promedio_con_descuento

FROM ecomerce_dwh.fact_ventas;
```

### 4. PERCENTILE_CONT, ¿Qué regiones presentan mejor desempeño comercial?
```
SELECT

    dg."Región",

    SUM(fv."Ventas") AS ventas_totales,

    SUM(fv."Beneficio") AS beneficio_total,

    PERCENTILE_CONT(0.5)
    WITHIN GROUP (
        ORDER BY fv."Beneficio"
    ) AS mediana_beneficio

FROM ecomerce_dwh.fact_ventas fv

JOIN ecomerce_dwh.dim_geografia dg
ON fv.id_geografia = dg.id_geografia

GROUP BY dg."Región"

ORDER BY beneficio_total DESC;
```

### 5. CTE + LAG(), ¿Qué modos de envío generan mayores costos logísticos?
```
WITH costos_envio AS (

    SELECT

        dt.anio,
        dt.mes,
        de."Modo de envío" AS modo_envio,

        SUM(fv."Costo de envío") AS costo_total

    FROM ecomerce_dwh.fact_ventas fv

    JOIN ecomerce_dwh.dim_envio de
        ON fv.id_envio = de.id_envio

    JOIN ecomerce_dwh.dim_tiempo dt
        ON fv.id_tiempo = dt.id_tiempo

    GROUP BY
        dt.anio,
        dt.mes,
        de."Modo de envío"

)

SELECT

    anio,
    mes,
    modo_envio,
    costo_total,

    LAG(costo_total) OVER (
        PARTITION BY modo_envio
        ORDER BY anio, mes
    ) AS costo_mes_anterior,

    costo_total -
    LAG(costo_total) OVER (
        PARTITION BY modo_envio
        ORDER BY anio, mes
    ) AS variacion_mensual

FROM costos_envio

ORDER BY
    modo_envio,
    anio,
    mes;
```

## 💻 Dashboard Interactivo
https://proyecto-final-en-proceso-xttekccq9sfhkj8yhyfosz.streamlit.app

## 🔎 Hallazgos importantes

### 1. 🧭 Inconsistencia estructural en la región de Canadá (dato nativo del dataset)
Durante la exploración inicial se identificó que la región de Canadá presenta una inconsistencia en su asignación organizacional, ya que no contaba con un responsable claramente definido dentro de la estructura original del dataset, no afecta los cálculos globales del modelo, ya que los agregados de ventas, beneficios y costos se mantienen consistentes. Sin embargo, sí representa una limitación estructural del dato original que podría influir en análisis más desagregados o en interpretaciones regionales específicas.

### 2. 🌍 Concentración de la rentabilidad en pocas regiones
La rentabilidad global está altamente concentrada en Europa Occidental y Asia Oriental, que juntas representan la mayor proporción del beneficio total, esto evidencia una dependencia del negocio en mercados específicos, lo que incrementa el riesgo ante fluctuaciones regionales.

### 3. 📦 Desbalance entre categorías de producto
Se observa un comportamiento desigual entre categorías:
- Tecnología → mayor rentabilidad y eficiencia
- Material de oficina → rendimiento estable y balanceado
- Mobiliario → alto volumen de ventas, pero baja rentabilidad

### 4. 💰 Dependencia de productos de alto valor unitario
Los productos más rentables corresponden principalmente a tecnología y equipos corporativos de alto ticket, esto implica que el modelo de negocio está orientado principalmente a transacciones de alto valor más que a volumen masivo de ventas.

### 5. 🚚 Crecimiento sostenido y volatilidad en costos logísticos
Los costos logísticos presentan una tendencia creciente en el tiempo, acompañada de variaciones mensuales significativas, sugiere que el crecimiento en ventas está directamente impactando la estructura de costos sin una optimización proporcional en eficiencia logística.

### 6. ⚡ Diferencias operativas por tipo de envío

Cada modo de envío presenta un comportamiento distinto:
- Clase estándar → mayor impacto en costos totales
- Urgente → alta volatilidad y picos operativos
- Segunda clase → comportamiento intermedio y estabilizador
- Mismo día → bajo volumen pero alta complejidad operativa

📌 Esto evidencia la necesidad de optimizar la planificación logística por tipo de servicio para reducir volatilidad y costos innecesarios.

## 📚 Referencias
- [Dataset inicial](https://www.kaggle.com/datasets/jaredrosas/global-superstore-orders-2016-es-esp)
- Material del módulo: [Guía 02](https://github.com/OscarAlvarezC/diplomado-bi-unam-iimas/blob/main/setup/02_dbeaver_conexion.md), [Tema 04](https://github.com/OscarAlvarezC/diplomado-bi-unam-iimas/tree/main/Tema-04), [rúbrica](https://github.com/OscarAlvarezC/diplomado-bi-unam-iimas/blob/main/anexos/rubrica_proyecto_final.md)
