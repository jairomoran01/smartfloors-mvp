# Guía de Generación e Importación de Datos

Esta guía explica cómo generar y cargar datos en el sistema SmartFloors.

## 📋 Tabla de Contenidos

1. [Generar Datos de Ejemplo](#generar-datos-de-ejemplo)
2. [Importar Datos desde JSON](#importar-datos-desde-json)
3. [Obtener Template JSON](#obtener-template-json)
4. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🎲 Generar Datos de Ejemplo

El sistema puede generar automáticamente datos de ejemplo para los 3 pisos. Esto es útil para pruebas y demostraciones.

### Endpoint

```
POST /api/v1/data/generate
```

### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `count` | integer | No | 30 | Número de lecturas a generar por piso (mín: 1, máx: 1000) |
| `interval_minutes` | integer | No | 1 | Intervalo entre lecturas en minutos (mín: 1, máx: 60) |
| `scenario` | string | No | "normal" | Escenario: "normal", "stress", o "mixed" |
| `start_time` | datetime | No | auto | Tiempo inicial (ISO 8601). Si no se especifica, se calcula automáticamente |

### Escenarios Disponibles

1. **normal**: Condiciones normales con variaciones pequeñas alrededor de valores óptimos
2. **stress**: Condiciones de estrés (temperatura alta, consumo alto)
3. **mixed**: Mezcla de condiciones normales y de estrés

### Ejemplo de Request

```bash
curl -X POST "http://localhost:8000/api/v1/data/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 30,
    "interval_minutes": 1,
    "scenario": "normal"
  }'
```

### Ejemplo de Response

```json
{
  "generated": 90,
  "start_time": "2025-11-12T10:00:00Z",
  "end_time": "2025-11-12T10:29:00Z",
  "created_ids": [1, 2, 3, 4, 5, ...]
}
```

**Nota**: El sistema genera `count × 3` lecturas (una por cada piso). Por ejemplo, si `count=30`, se generan 90 lecturas en total (30 por piso).

### Ejemplo con Python

```python
import requests

url = "http://localhost:8000/api/v1/data/generate"
payload = {
    "count": 30,
    "interval_minutes": 1,
    "scenario": "normal"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Ejemplo con JavaScript/Node.js

```javascript
const axios = require('axios');

async function generateData() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/data/generate', {
      count: 30,
      interval_minutes: 1,
      scenario: 'normal'
    });
    console.log('Datos generados:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

generateData();
```

---

## 📥 Importar Datos desde JSON

Puedes importar datos desde un archivo JSON con el formato correcto.

### Endpoint

```
POST /api/v1/data/import
```

### Formato del JSON

El JSON debe tener la siguiente estructura:

```json
{
  "readings": [
    {
      "timestamp": "2025-11-12T10:00:00Z",
      "edificio": "A",
      "piso": 1,
      "temp_c": 24.5,
      "humedad_pct": 60.0,
      "energia_kw": 12.5
    },
    {
      "timestamp": "2025-11-12T10:01:00Z",
      "edificio": "A",
      "piso": 1,
      "temp_c": 24.6,
      "humedad_pct": 60.2,
      "energia_kw": 12.6
    }
  ]
}
```

### Campos Requeridos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `timestamp` | string (ISO 8601) | Fecha y hora de la lectura |
| `edificio` | string | Código del edificio (default: "A") |
| `piso` | integer | Número de piso (1, 2, o 3) |
| `temp_c` | float | Temperatura en grados Celsius |
| `humedad_pct` | float | Humedad relativa en porcentaje (0-100) |
| `energia_kw` | float | Consumo energético en kilovatios |

### Ejemplo de Request con cURL

```bash
curl -X POST "http://localhost:8000/api/v1/data/import" \
  -H "Content-Type: application/json" \
  -d @example_data.json
```

O directamente:

```bash
curl -X POST "http://localhost:8000/api/v1/data/import" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "timestamp": "2025-11-12T10:00:00Z",
        "edificio": "A",
        "piso": 1,
        "temp_c": 24.5,
        "humedad_pct": 60.0,
        "energia_kw": 12.5
      }
    ]
  }'
```

### Ejemplo de Response

```json
{
  "imported": 9,
  "errors": 0,
  "error_details": [],
  "created_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9]
}
```

Si hay errores:

```json
{
  "imported": 7,
  "errors": 2,
  "error_details": [
    "Lectura 3: Piso debe ser 1, 2 o 3, recibido: 4",
    "Lectura 8: timestamp debe ser string ISO o datetime"
  ],
  "created_ids": [1, 2, 4, 5, 6, 7, 9]
}
```

### Ejemplo con Python

```python
import requests
import json

# Cargar datos desde archivo
with open('example_data.json', 'r') as f:
    data = json.load(f)

# O crear datos directamente
data = {
    "readings": [
        {
            "timestamp": "2025-11-12T10:00:00Z",
            "edificio": "A",
            "piso": 1,
            "temp_c": 24.5,
            "humedad_pct": 60.0,
            "energia_kw": 12.5
        },
        {
            "timestamp": "2025-11-12T10:01:00Z",
            "edificio": "A",
            "piso": 1,
            "temp_c": 24.6,
            "humedad_pct": 60.2,
            "energia_kw": 12.6
        }
    ]
}

url = "http://localhost:8000/api/v1/data/import"
response = requests.post(url, json=data)
print(response.json())
```

### Ejemplo con JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

// Opción 1: Cargar desde archivo
const data = JSON.parse(fs.readFileSync('example_data.json', 'utf8'));

// Opción 2: Crear datos directamente
const data = {
  readings: [
    {
      timestamp: "2025-11-12T10:00:00Z",
      edificio: "A",
      piso: 1,
      temp_c: 24.5,
      humedad_pct: 60.0,
      energia_kw: 12.5
    }
  ]
};

async function importData() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/data/import', data);
    console.log('Datos importados:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

importData();
```

---

## 📄 Obtener Template JSON

Puedes obtener un template JSON para ver el formato correcto de los datos.

### Endpoint

```
GET /api/v1/data/export-template
```

### Ejemplo de Request

```bash
curl "http://localhost:8000/api/v1/data/export-template"
```

### Ejemplo de Response

```json
{
  "readings": [
    {
      "timestamp": "2025-11-12T10:00:00Z",
      "edificio": "A",
      "piso": 1,
      "temp_c": 24.5,
      "humedad_pct": 60.0,
      "energia_kw": 12.5
    },
    {
      "timestamp": "2025-11-12T10:01:00Z",
      "edificio": "A",
      "piso": 1,
      "temp_c": 24.6,
      "humedad_pct": 60.2,
      "energia_kw": 12.6
    }
  ]
}
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Generar 60 lecturas para pruebas

```bash
curl -X POST "http://localhost:8000/api/v1/data/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 60,
    "interval_minutes": 1,
    "scenario": "normal"
  }'
```

Esto generará 180 lecturas (60 por cada uno de los 3 pisos), cubriendo las últimas 60 minutos.

### Ejemplo 2: Generar datos de estrés para pruebas de alertas

```bash
curl -X POST "http://localhost:8000/api/v1/data/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 30,
    "interval_minutes": 1,
    "scenario": "stress"
  }'
```

Esto generará datos con temperaturas altas y consumo elevado, lo que debería generar alertas.

### Ejemplo 3: Importar datos históricos desde archivo

1. Crea un archivo `datos_historicos.json`:

```json
{
  "readings": [
    {
      "timestamp": "2025-11-12T08:00:00Z",
      "edificio": "A",
      "piso": 1,
      "temp_c": 23.5,
      "humedad_pct": 55.0,
      "energia_kw": 11.5
    },
    {
      "timestamp": "2025-11-12T08:01:00Z",
      "edificio": "A",
      "piso": 1,
      "temp_c": 23.6,
      "humedad_pct": 55.2,
      "energia_kw": 11.6
    }
  ]
}
```

2. Importa los datos:

```bash
curl -X POST "http://localhost:8000/api/v1/data/import" \
  -H "Content-Type: application/json" \
  -d @datos_historicos.json
```

### Ejemplo 4: Script Python completo para generar e importar

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Generar datos de ejemplo
print("Generando datos de ejemplo...")
response = requests.post(
    f"{BASE_URL}/api/v1/data/generate",
    json={
        "count": 30,
        "interval_minutes": 1,
        "scenario": "normal"
    }
)
print(f"Datos generados: {response.json()}")

# 2. Obtener template
print("\nObteniendo template...")
response = requests.get(f"{BASE_URL}/api/v1/data/export-template")
template = response.json()
print(f"Template obtenido: {len(template['readings'])} lecturas de ejemplo")

# 3. Crear datos personalizados
custom_data = {
    "readings": [
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat() + "Z",
            "edificio": "A",
            "piso": (i % 3) + 1,
            "temp_c": 24.0 + (i * 0.1),
            "humedad_pct": 55.0 + (i * 0.2),
            "energia_kw": 12.0 + (i * 0.1)
        }
        for i in range(10)
    ]
}

# 4. Importar datos personalizados
print("\nImportando datos personalizados...")
response = requests.post(
    f"{BASE_URL}/api/v1/data/import",
    json=custom_data
)
print(f"Datos importados: {response.json()}")
```

### Ejemplo 5: Usando Postman o Thunder Client

1. **Generar datos:**
   - Método: `POST`
   - URL: `http://localhost:8000/api/v1/data/generate`
   - Body (JSON):
   ```json
   {
     "count": 30,
     "interval_minutes": 1,
     "scenario": "normal"
   }
   ```

2. **Importar datos:**
   - Método: `POST`
   - URL: `http://localhost:8000/api/v1/data/import`
   - Body (JSON): Usa el contenido de `example_data.json`

3. **Obtener template:**
   - Método: `GET`
   - URL: `http://localhost:8000/api/v1/data/export-template`

---

## ⚠️ Notas Importantes

1. **Validación automática**: El sistema valida automáticamente:
   - Piso debe ser 1, 2, o 3
   - Temperatura debe estar en rango razonable
   - Humedad debe estar entre 0-100%
   - Timestamp debe ser válido

2. **Alertas automáticas**: Después de importar o generar datos, el sistema verifica automáticamente si se deben generar alertas según los umbrales configurados.

3. **Datos duplicados**: Si intentas importar una lectura con el mismo `timestamp`, `edificio` y `piso`, puede generar un error de duplicado.

4. **Rendimiento**: Para grandes volúmenes de datos (más de 1000 lecturas), considera importar en lotes.

---

## 🔍 Verificar Datos Importados

Después de generar o importar datos, puedes verificar que se cargaron correctamente:

```bash
# Ver lecturas recientes
curl "http://localhost:8000/api/v1/readings?limit=10"

# Ver lectura actual del piso 1
curl "http://localhost:8000/api/v1/readings/floors/1/current"

# Ver resumen del dashboard
curl "http://localhost:8000/api/v1/dashboard/summary"
```

---

## 📚 Recursos Adicionales

- Documentación completa de la API: `http://localhost:8000/docs`
- Archivo de ejemplo: `backend/example_data.json`
- README del backend: `backend/README.md`

