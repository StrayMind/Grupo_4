# Grupo_4
Gestión de datos para IA

# MVP DataOps CreditCardaFraud

Repositorio piloto para preparar, probar y documentar un entorno técnico reproducible para soluciones de datos e IA.

## Objetivo
Contar con una base técnica simple y replicable para que los grupos de estudiantes puedan trabajar con:
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
- Modelo de clasificación binaria con Regresión Logística

## Estructura del proyecto
```text
mvp-dataops-CreditCardFraud/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ db.py│ 
├─ scripts/
│  ├─ load_fraudtest_csv.py
│  └─ limpieza_fraud_pipeline.py
│  └─ validate_frautest.py
├─ tests/
│  └─ test_health.py
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ data/
  └─ 02_fraudTest.csv
├─ .env.example
├─ .gitignore
├─ .dockerignore
├─ Dockerfile
├─ README.md
├─ render.yaml
└─ requirements.txt
```

## Flujo implementado
1. Se dispone de un archivo CSV de ejemplo en `data/01_fraudtest.csv`
2. Se crea una tabla destino en Supabase: `public.fraudtest_demo`
3. Un script Python carga los datos del Excel a Supabase
4. La API consulta esos datos y los expone en JSON
5. Se generan estadísticas básicas del dataset
