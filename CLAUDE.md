# Product Requirements Document (PRD)
## SmartFloors: Sistema de Monitoreo y Alertas por Piso
---
## 1. Resumen Ejecutivo
**Proyecto:** SmartFloors MVP - Hackathon
**Duración:** 11-12 noviembre 2025 (24 horas)
**Equipo:** 3 personas
**Objetivo:** Sistema de monitoreo predictivo de condiciones ambientales y eléctricas para Edificio A (3 pisos) con alertas inteligentes y recomendaciones accionables.
---
## 2. Tech Stack
### Backend
*   **Lenguaje:** Python 3.11+
*   **Framework:** FastAPI
*   **Predicción:** scikit-learn, statsmodels (ARIMA)
*   **Procesamiento de datos:** pandas, numpy
*   **Tareas asíncronas:** Celery + Redis (para notificaciones)
*   **IA/Recomendaciones:** Gemini API
### Frontend
*   **Framework:** React 18 + Vite
*   **UI Components:** shadcn/ui + TailwindCSS
*   **Gráficos:** Chart.js
*   **Estado:** React Query + Zustand
*   **HTTP Client:** Axios
### Base de Datos
*   **Principal:** PostgreSQL 15+
*   **Cache:** Redis (para métricas en tiempo real)
### Infraestructura (Gratuita)
*   **Backend + DB:**
	*   Railway.app (PostgreSQL + FastAPI deployment)
	*   Render.com (alternativa)
*   **Frontend:**
	*   Vercel
*   **Redis:**
	*   Redis Labs (free tier) o Upstash
### DevOps
*   **Contenedores:** Docker + Docker Compose
*   **CI/CD:** GitHub Actions
*   **API Testing:** Postman/Thunder Client
*   **Versionamiento:** Git + GitHub
---
## 3. Dependencias Principales
### Backend (`requirements.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
statsmodels==0.14.0
python-dotenv==1.0.0
httpx==0.25.2
celery==5.3.4
redis==5.0.1
python-multipart==0.0.6
```
### Frontend (`package.json` - principales)
```
{
  "react": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "chart.js": "^4.0.0",
  "axios": "^1.6.2",
  "@tanstack/react-query": "^5.8.0",
  "zustand": "^4.4.7",
  "tailwindcss": "^3.3.5",
  "lucide-react": "^0.292.0"
}
```
---
## 4. APIs del Sistema
### 4.1 API REST Endpoints
#### Ingesta de Datos
```
POST /api/v1/readings
Body: {
  "timestamp": "2025-11-11T10:30:00Z",
  "edificio": "A",
  "piso": 1,
  "temp_C": 25.5,
  "humedad_pct": 60.0,
  "energia_kW": 12.5
}
Response: 201 Created




POST /api/v1/readings/batch
Body: [
  { /* múltiples lecturas */ }
]
Response: 201 Created
```
#### Consultas
```
GET /api/v1/readings?piso=1&start=2025-11-11T00:00:00Z&end=2025-11-11T23:59:59Z
Response: { "data": [...], "total": 180 }




GET /api/v1/floors/{piso}/current
Response: {
  "piso": 1,
  "temp_C": 25.5,
  "humedad_pct": 60.0,
  "energia_kW": 12.5,
  "timestamp": "...",
  "status": "OK"
}
```
#### Predicciones
```
GET /api/v1/predictions/{piso}?horizon=60
Response: {
  "piso": 1,
  "predictions": {
    "temperatura": [
      {"timestamp": "...", "value": 26.2, "confidence_interval": [25.8, 26.6]},
      ...
    ],
    "humedad": [...],
    "riesgo_termico": "medio"
  }
}
```
#### Alertas
```
GET /api/v1/alerts?piso=1&nivel=critica&limit=50
Response: {
  "alerts": [
    {
      "id": "uuid",
      "timestamp": "...",
      "piso": 2,
      "variable": "temperatura",
      "nivel": "critica",
      "valor_actual": 30.5,
      "umbral": 29.9,
      "recomendacion": "Ajustar temperatura del Piso 2 a 24°C en los próximos 15 min.",
      "explicacion": "Temperatura supera umbral crítico con consumo energético alto"
    }
  ]
}




POST /api/v1/alerts/{alert_id}/acknowledge
Response: 200 OK




GET /api/v1/alerts/export?format=csv
Response: CSV file download
```
#### Dashboard
```
GET /api/v1/dashboard/summary
Response: {
  "pisos": [
    {
      "piso": 1,
      "estado": "OK",
      "resumen": "Condiciones normales",
      "metricas": {...},
      "alertas_activas": 0
    },
    ...
  ],
  "alertas_recientes": [...],
  "timestamp": "..."
}
```
#### Notificaciones (Bonus)
```
POST /api/v1/notifications/subscribe
Body: {
  "email": "user@example.com",
  "pisos": [1, 2, 3],
  "niveles": ["media", "critica"]
}
```
#### Simulación de Datos
```
POST /api/v1/simulator/start
Body: {
  "duration_minutes": 120,
  "interval_seconds": 60,
  "scenario": "normal" | "stress" | "anomaly"
}
Response: { "simulator_id": "uuid", "status": "running" }




POST /api/v1/simulator/stop
```
---
## 5. Esquema de Base de Datos
### Diagrama Relacional
```
-- Tabla principal de lecturas
CREATE TABLE lecturas (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    edificio VARCHAR(10) NOT NULL DEFAULT 'A',
    piso INTEGER NOT NULL CHECK (piso IN (1, 2, 3)),
    temp_c DECIMAL(5,2) NOT NULL,
    humedad_pct DECIMAL(5,2) NOT NULL,
    energia_kw DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_reading UNIQUE (timestamp, edificio, piso)
);

-- Índices para consultas rápidas
CREATE INDEX idx_lecturas_timestamp ON lecturas(timestamp DESC);
CREATE INDEX idx_lecturas_piso_timestamp ON lecturas(piso, timestamp DESC);
CREATE INDEX idx_lecturas_edificio_piso ON lecturas(edificio, piso);

-- Tabla de alertas
CREATE TABLE alertas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    piso INTEGER NOT NULL CHECK (piso IN (1, 2, 3)),
    variable VARCHAR(50) NOT NULL, -- temperatura, humedad, energia, riesgo_combinado
    nivel VARCHAR(20) NOT NULL CHECK (nivel IN ('informativa', 'media', 'critica')),
    valor_actual DECIMAL(8,2),
    umbral DECIMAL(8,2),
    recomendacion TEXT NOT NULL,
    explicacion TEXT,
    estado VARCHAR(20) DEFAULT 'activa' CHECK (estado IN ('activa', 'reconocida', 'resuelta')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_alertas_timestamp ON alertas(timestamp DESC);
CREATE INDEX idx_alertas_piso_estado ON alertas(piso, estado);
CREATE INDEX idx_alertas_nivel ON alertas(nivel);

-- Tabla de predicciones (opcional, para auditoría)
CREATE TABLE predicciones (
    id SERIAL PRIMARY KEY,
    timestamp_generacion TIMESTAMPTZ NOT NULL,
    timestamp_prediccion TIMESTAMPTZ NOT NULL,
    piso INTEGER NOT NULL,
    variable VARCHAR(50) NOT NULL,
    valor_predicho DECIMAL(8,2) NOT NULL,
    intervalo_confianza_min DECIMAL(8,2),
    intervalo_confianza_max DECIMAL(8,2),
    modelo VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predicciones_piso_timestamp ON predicciones(piso, timestamp_prediccion);

-- Tabla de umbrales configurables
CREATE TABLE umbrales (
    id SERIAL PRIMARY KEY,
    variable VARCHAR(50) NOT NULL,
    nivel VARCHAR(20) NOT NULL,
    valor_min DECIMAL(8,2),
    valor_max DECIMAL(8,2),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Datos iniciales de umbrales
INSERT INTO umbrales (variable, nivel, valor_min, valor_max, descripcion) VALUES
('temperatura', 'informativa', 26.0, 27.9, 'Temperatura ligeramente elevada'),
('temperatura', 'media', 28.0, 29.9, 'Temperatura alta, requiere atención'),
('temperatura', 'critica', 30.0, NULL, 'Temperatura crítica, acción inmediata'),
('humedad', 'informativa_baja', NULL, 25.0, 'Humedad baja'),
('humedad', 'informativa_alta', 70.0, NULL, 'Humedad alta'),
('humedad', 'media_baja', NULL, 22.0, 'Humedad muy baja'),
('humedad', 'media_alta', 75.0, NULL, 'Humedad muy alta'),
('humedad', 'critica_baja', NULL, 20.0, 'Humedad críticamente baja'),
('humedad', 'critica_alta', 80.0, NULL, 'Humedad críticamente alta'),
('energia', 'informativa', 15.0, 20.0, 'Consumo elevado'),
('energia', 'media', 20.0, 25.0, 'Consumo alto'),
('energia', 'critica', 25.0, NULL, 'Consumo crítico');

-- Tabla de suscripciones de notificaciones (bonus)
CREATE TABLE suscripciones (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    pisos INTEGER[] NOT NULL,
    niveles VARCHAR(20)[] NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_email UNIQUE (email)
);

-- Vista materializada para dashboard (performance)
CREATE MATERIALIZED VIEW dashboard_metricas AS
SELECT 
    piso,
    DATE_TRUNC('minute', timestamp) as minuto,
    AVG(temp_c) as temp_avg,
    MAX(temp_c) as temp_max,
    MIN(temp_c) as temp_min,
    AVG(humedad_pct) as humedad_avg,
    AVG(energia_kw) as energia_avg,
    SUM(energia_kw) as energia_total
FROM lecturas
WHERE timestamp >= NOW() - INTERVAL '4 hours'
GROUP BY piso, minuto;

CREATE INDEX idx_dashboard_metricas ON dashboard_metricas(piso, minuto DESC);

-- Función para refrescar vista materializada (llamar cada 5 minutos)
CREATE OR REPLACE FUNCTION refresh_dashboard_metricas()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_metricas;
END;
$$ LANGUAGE plpgsql;
```
### Diagrama Visual
```
┌─────────────────┐
│    lecturas  │
├─────────────────┤
│ id (PK)      │
│ timestamp    │
│ edificio     │
│ piso         │
│ temp_c       │
│ humedad_pct  │
│ energia_kw   │
│ created_at   │
└─────────────────┘
        │
        │ (genera)
        ▼
┌─────────────────┐
│    alertas   │
├─────────────────┤
│ id (PK)      │
│ timestamp    │
│ piso         │
│ variable     │
│ nivel        │
│ valor_actual │
│ umbral       │
│ recomendacion│
│ explicacion  │
│ estado       │
└─────────────────┘
        │
        │ (se basa en)
        ▼
┌─────────────────┐
│   umbrales   │
├─────────────────┤
│ id (PK)      │
│ variable     │
│ nivel        │
│ valor_min    │
│ valor_max    │
│ descripcion  │
└─────────────────┘
```
---
## 6. Alcance del Proyecto
### ✅ Dentro del Alcance (MVP - 24 horas)
#### Funcionalidades Core
1.  **Ingesta de datos simulados**
	*   Endpoint para recibir lecturas (temp, humedad, energía)
	*   Simulador automático con datos realistas
	*   Validación de datos de entrada
1.  **Almacenamiento**
	*   Base de datos PostgreSQL
	*   Modelo de datos relacional
	*   Índices optimizados para consultas
1.  **Predicción a +60 minutos**
	*   Temperatura por piso
	*   Humedad por piso
	*   Riesgo térmico combinado (temp + energía)
	*   Modelo: Regresión lineal o promedio móvil (simple y rápido)
1.  **Sistema de alertas**
	*   Detección basada en umbrales configurados
	*   3 niveles: Informativa, Media, Crítica
	*   Alertas preventivas basadas en predicciones
1.  **Recomendaciones IA**
	*   Integración con API de Gemini
	*   Recomendaciones contextualizadas (1-2 líneas)
	*   Explicabilidad de alertas
1.  **Dashboard Web**
	*   Tarjetas de estado por piso
	*   Gráficos de tendencia (últimas 2-4 horas)
	*   Tabla de alertas con filtros
	*   Actualización en tiempo real (polling cada 30s)
1.  **Exportación de alertas**
	*   Descarga en formato CSV
	*   Filtros aplicables
#### Infraestructura
*   Deployment en Railway/Render (backend + DB)
*   Frontend en Vercel
*   Todo accesible vía URLs públicas
*   Documentación API con Swagger/OpenAPI
### ⚠️ Dentro del Alcance (Bonificaciones - Si da tiempo)
1.  **Notificaciones automáticas**
	*   Suscripción por email
	*   Alertas medias/críticas vía email
	*   Celery + Redis para tareas asíncronas
1.  **Reproducción de datos históricos**
	*   Endpoint para replay de datos
	*   Análisis retrospectivo
### ❌ Fuera del Alcance
1.  **Hardware/Sensores reales** - Solo datos simulados
1.  **Autenticación/Autorización** - Sin login ni permisos
1.  **Multi-edificio** - Solo Edificio A
1.  **Múltiples modelos ML** - Un solo modelo de predicción
1.  **Aplicación móvil** - Solo web
1.  **Integración con sistemas HVAC reales**
1.  **Machine Learning avanzado** - Modelos complejos (LSTM, etc.)
1.  **Análisis histórico profundo** - Foco en tiempo real
1.  **Multi-idioma** - Solo español
1.  **Tests automatizados completos** - Tests básicos solamente
1.  **Optimización de rendimiento avanzada**
1.  **Backup y recuperación automática**
---
## 7. User Flow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO FINAL                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                1. LANDING / DASHBOARD             │
│  - Visualiza 3 tarjetas de piso (Piso 1, 2, 3)    │
│  - Estado general: OK / Informativa / Media / Crítica       │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
    ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │ Ver Detalles  │ │  Alertas │ │   Filtrar    │
    │   por Piso    │ │  Activas │ │  Dashboard   │
    └───────────────┘ └──────────┘ └──────────────┘
                │           │           │
                └───────────┼───────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           2. VISTA DETALLADA DE PISO              │
│  - Gráficos de tendencia (temp, humedad, energía) │
│  - Últimas 2-4 horas                              │
│  - Valores actuales en tiempo real                │
│  - Predicciones a +60 min                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           3. TABLA DE ALERTAS                     │
│  Filtros disponibles:                             │
│  - Por piso (1, 2, 3, Todos)                      │
│  - Por nivel (OK, Informativa, Media, Crítica)    │
│  - Por fecha/rango                                │
│                                                   │
│  Columnas:                                        │
│  - Timestamp                                      │
│  - Piso                                           │
│  - Variable (temp/humedad/energía)                │
│  - Nivel                                          │
│  - Recomendación                                  │
│  - [Ver Explicación] [Reconocer]                  │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │         │         │
                ▼        ▼         ▼
    ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │ Ver        │ │ Reconocer││   Exportar │
    │ Explicación│ │  Alerta  ││     CSV    │
    └───────────────┘ └──────────┘ └──────────────┘
                │           │        │
                └───────────┼───────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           4. MODAL DE EXPLICACIÓN (Bonus)                    │
│  - Contexto de la alerta                                     │
│  - Por qué se generó                                         │
│  - Datos que la sustentaron                                  │
│  - Recomendación detallada                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│      5. CONFIGURACIÓN DE NOTIFICACIONES (Bonus)              │
│  - Suscribirse con email                                     │
│  - Seleccionar pisos a monitorear                           │
│  - Seleccionar niveles de alerta                            │
└─────────────────────────────────────────────────────────────┘
```
### Flow Backend (Procesamiento Automático)
```
┌─────────────────┐
│  Simulador de│
│     Datos    │ (Genera lecturas cada 1 min)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  POST /readings │
│   (Ingesta)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ (Almacena lecturas)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Worker/Celery  │ (Procesa cada minuto)
│   (async task)  │
└─────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Predictor│ │ Detector │
│ Model  │ │ Umbrales │
└────────┘ └──────────┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│ Genera Alerta?  │
│   (Si/No)       │
└─────────────────┘
         │ Sí
         ▼
┌─────────────────┐
│  API IA Gemini  │ (Genera recomendación)
│   /GPT (prompt) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  INSERT alerta  │
│  + explicación  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Enviar Email?   │ (Si bonus activado)
│   (Celery task) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │ (Polling actualiza UI)
│   actualizado   │
└─────────────────┘
```
---
## 8. Arquitectura del Sistema
### Diagrama de Alto Nivel
```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                              │
│                    (React + Vercel)                           │
│  - Dashboard  - Gráficos  - Alertas  - Filtros              │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS / REST API
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    API GATEWAY / BACKEND                      │
│                   (FastAPI + Railway)                         │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐        │
│  │  Ingesta    │  │  Predicción  │  │   Alertas   │        │
│  │   Module    │  │    Module    │  │   Module    │        │
│  └─────────────┘  └──────────────┘  └─────────────┘        │
│         │                │                  │                 │
│         └────────────────┼──────────────────┘                │
│                          │                                    │
└──────────────────────────┼───────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │  Gemini API  │
│  (Railway)   │  │  (Upstash)   │  │  (Externa)   │
│              │  │              │  │              │
│ - lecturas   │  │ - cache      │  │ - IA reco-   │
│ - alertas    │  │ - métricas   │  │   mendaciones│
│ - umbrales   │  │ - jobs queue │  │ - explicación│
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────┐
        │    Celery    │
        │   Workers    │
        │              │
        │ - Predictor  │
        │ - Alerts     │
        │ - Notif.     │
        └──────────────┘
```
---
## 9. Estrategia de Desarrollo (Scrum - 24 horas)
### Equipo de 3 Personas - Distribución de Roles
#### **Persona 1: Backend/Data Engineer**
*   Setup inicial de FastAPI y PostgreSQL
*   Modelos de datos (SQLAlchemy)
*   Endpoints de ingesta
*   Sistema de alertas y umbrales
*   Integración con API de IA
#### **Persona 2: ML/Data Scientist**
*   Simulador de datos realistas
*   Modelo de predicción (temp, humedad)
*   Lógica de detección de anomalías
*   Integración predictor con backend
*   Análisis de riesgos combinados
#### **Persona 3: Frontend Developer**
*   Setup de React + componentes UI
*   Dashboard y tarjetas de piso
*   Gráficos con Recharts
*   Tabla de alertas con filtros
*   Integración con API REST
### Sprints (Bloques de 4-6 horas)
#### **Sprint 1: Setup y Foundation (Horas 1-6)**
*   [ ] Setup repositorio Git
*   [ ] Dockerizar backend + PostgreSQL
*   [ ] Deploy inicial en Railway/Render
*   [ ] Crear esquema de DB y migrar
*   [ ] Setup React + deploy en Vercel
*   [ ] Endpoint básico de ingesta funcionando
*   [ ] Simulador básico de datos
**Entregable:** Sistema desplegado con ingesta funcionando
#### **Sprint 2: Core Features (Horas 7-12)**
*   [ ] Endpoints CRUD completos
*   [ ] Modelo de predicción implementado
*   [ ] Sistema de detección de umbrales
*   [ ] Dashboard mostrando datos en tiempo real
*   [ ] Gráficos de tendencia funcionando
*   [ ] Tabla de alertas básica
**Entregable:** MVP funcional sin IA
#### **Sprint 3: Alertas e IA (Horas 13-18)**
*   [ ] Integración con API de Gemini
*   [ ] Generación de recomendaciones IA
*   [ ] Sistema de alertas completo
*   [ ] Explicabilidad de alertas
*   [ ] Filtros en tabla de alertas
*   [ ] Exportación CSV
**Entregable:** Sistema completo con IA
#### **Sprint 4: Polish y Bonus (Horas 19-24)**
*   [ ] Notificaciones por email (si da tiempo)
*   [ ] UI/UX mejorado
*   [ ] Manejo de errores robusto
*   [ ] Documentación de API (Swagger)
*   [ ] Testing básico
*   [ ] Preparación de demo
*   [ ] Slides de presentación
**Entregable:** Sistema pulido + presentación
### Daily Scrum (Cada 6 horas)
*   ¿Qué hicimos?
*   ¿Qué haremos?
*   ¿Impedimentos?
*   Ajustar prioridades
---
## 10. Criterios de Éxito (Alineados con Evaluación)
### Arquitectura / Estructura del Código (20%)
*   ✅ Separación clara de concerns (API, lógica, datos)
*   ✅ Código modular y reutilizable
*   ✅ Uso de design patterns apropiados
*   ✅ Comentarios y documentación inline
*   ✅ Manejo de errores consistente
### Gestión de Equipo (10%)
*   ✅ Uso de Git con commits descriptivos
*   ✅ Tablero Trello/GitHub Projects visible
*   ✅ División clara de tareas
*   ✅ Comunicación en Slack/Discord documentada
### Funcionalidad (20%)
*   ✅ Ingesta de datos funcionando
*   ✅ Predicciones a +60 min precisas
*   ✅ Alertas generadas correctamente
*   ✅ Dashboard interactivo y responsivo
*   ✅ Exportación CSV funcional
### Conceptos y Sustentación (15%)
*   ✅ Justificar elección de modelo predictivo
*   ✅ Explicar arquitectura de microservicios
*   ✅ Fundamentar umbrales seleccionados
*   ✅ Demostrar comprensión de HVAC
### Entendimiento del Problema (20%)
*   ✅ Solución directamente ataca el problema
*   ✅ Alertas son accionables y relevantes
*   ✅ Recomendaciones contextualizadas
*   ✅ Sistema adaptable a nuevos pisos/edificios
### UX y Usabilidad (15%)
*   ✅ Navegación intuitiva
*   ✅ Información clara y sin sobrecarga
*   ✅ Colores consistentes con niveles de alerta
*   ✅ Responsive design
*   ✅ Carga rápida de datos
---
