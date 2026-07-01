# Grupo_4
Gestión de datos para IA

# MVP DataOps CreditCardaFraud

Repositorio para preparar, probar y documentar un entorno técnico reproducible para soluciones de datos e IA.

## Objetivo
Entorno tecnico reproducible para entrenar un modelo IA que detecte fraudes de tarjetas de credito trabajando con:
- Python 3
- FastAPI
- Docker
- Git y GitHub
- GitHub Actions
- Render
- Supabase (PostgreSQL)
- Scikit-learn para un clasificador binario simple

## Arquitectura del MVP
La solución implementa una arquitectura IA híbrida simple:
![Arquitectura del MVP](images/Arquitectura.png)
- Aplicación Python dockerizada
- API con FastAPI
- CI/CD con GitHub Actions
- Despliegue en Render
- Base de datos PostgreSQL en Supabase
- Modelo de clasificación binaria con Arbol de decision

## Estructura del proyecto
```text
mvp-dataops-CreditCardFraud/
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ app/
│  ├─ __init__.py
│  ├─ db.py
│  ├─ main.py
│  └─ predict.py
├─ artifacts/
│  ├─ fraude_metrics.json
│  └─ fraude_model.joblib
├─ data/
  └─ 02_fraudTest.csv (url del drive en donde esta el csv)
├─ scripts/
│  ├─ correr_pipeline.py
│  ├─ limpieza_fraud_pipeline.py
│  ├─ load_fraudtest_csv.py
│  ├─ train_fraud_model.py
│  └─ validate_frautest.py
├─ tests/
│  └─ test_health.py
├─ .dockerignore
├─ .env.example
├─ .gitignore
├─ Dockerfile
├─ README.md
├─ render.yaml
└─ requirements.txt
```

## Flujo implementado
1. Se dispone de un archivo CSV de ejemplo en data/02_fraudTest.csv
2. Se validan y limpian los datos mediante scripts
3. Se crea una tabla destino en Supabase: `public.fraudtest_demo`
4. Un script Python carga los datos del CSV a Supabase
5. Se entrena un modelo de clasificación binaria para detectar `FRAUDE`
6. Se guardan los artefactos del modelo en artifacts/
7. La API consulta esos datos y los expone en JSON
8. El proyecto se despliega usando Render y Power Bi

## Dataset y variable objetivo
Se utliza el dataset de `fraudeTest` y la variable objetivo es:

-  `is_fraud` → valores `NORMAL` / `FRAUDE`

Para el MVP se implemento el clasificador binario con el **Arbol de decision**.

## Endpoints actuales
- `GET /` : verifica que la API esté activa
- `GET /health` : verifica salud general
- `GET /db-health` : verifica conexión a Supabase
- `GET /fraudetest-demo?limit=20` : devuelve registros desde la tabla `fraudtest_demo`
- `GET /fraudetest-demo/stats` : devuelve estadísticas básicas del dataset
- `POST /predict-fraude` : devuelve la predicción de fraude usando el modelo entrenado

## Ejecución local
1. Clonar el repositorio
2. Crear archivo `.env` a partir de `.env.example`
3. Activar entorno virtual
4. Instalar dependencias
5. Ejecutar:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Pruebas locales de API
Probar en navegador o herramienta similar:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/db-health
http://127.0.0.1:8000/fraudetest-demo?limit=5
http://127.0.0.1:8000/fraudetest-demo/stats
http://127.0.0.1:8000/docs
```

## Carga de datos desde Excel
El script de carga es:

```bash
python scripts/load_fraudtest_csv.py
```

### Qué hace
- lee `data/02_fraudTest.csv`
- valida columnas esperadas
- limpia la tabla `public.fraudtest_demo`
- inserta nuevamente los registros

## SQL base de la tabla
La tabla se crea con el archivo:

```text
sql/01_create_fraudtest_demo_table.sql
```

Ese archivo debe ejecutarse en **Supabase > SQL Editor** antes de correr la carga del CSV.

## Estadísticas del dataset
El endpoint:

```text
GET /fraudtest-demo/stats
```

devuelve:


## Entrenamiento del modelo
El script de entrenamiento es:

```bash
python scripts/train_fraude_model.py
```

### Qué hace
- lee los datos desde `public.postulaciones_demo`
- prepara variables categóricas y numéricas
- usa `ColumnTransformer` + `OrdinalEncoder`
- divide train/test con `stratify=y`
- entrena una `DecisionTreeClassifier`
- guarda el modelo y las métricas

### Artefactos generados
```text
artifacts/fraude_model.joblib
artifacts/fraude_metrics.json
```

## Resultado base del modelo
En la versión actual del MVP se obtuvo aproximadamente:

- `accuracy`: 0.98

La interpretación general es:
- buen desempeño para identificar la clase `Normal`
- desempeño demasiado bajo identificar `Fraude`

## Predicción
El endpoint:

```text
POST /predict-matriculado
```

espera un JSON con estas variables:
```text
payload = {
        "merchant": "58",
        "category": "12",
        "amt": 286.50,
        "street": "67",
        "city": "8",
        "state": "9",
        "zip": 62701,
        "lat": 39.7817,
        "long": -89.6501,
        "job" : "24",
        "merch_lat": 39.8000,
        "merch_long": -89.6000
    }
```
