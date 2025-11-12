import httpx
from typing import Tuple, Optional
from app.config import settings


class AIService:
    """Servicio para integración con Gemini API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    def generate_alert_recommendation(
        self,
        piso: int,
        variable: str,
        nivel: str,
        valor_actual: float,
        umbral: float,
        temp_c: float,
        humedad_pct: float,
        energia_kw: float
    ) -> Tuple[str, str]:
        """Genera recomendación y explicación usando Gemini API"""
        
        # Si no hay API key, usar recomendaciones predefinidas
        if not self.api_key:
            return self._get_fallback_recommendation(
                piso, variable, nivel, valor_actual, umbral
            )
        
        prompt = f"""Eres un experto en gestión de edificios inteligentes. 
Genera una recomendación accionable y breve (1-2 líneas) para una alerta de monitoreo.

Contexto:
- Piso: {piso}
- Variable alertada: {variable}
- Nivel de alerta: {nivel}
- Valor actual: {valor_actual}
- Umbral: {umbral}
- Temperatura actual: {temp_c}°C
- Humedad actual: {humedad_pct}%
- Consumo energético: {energia_kw} kW

Genera:
1. Una recomendación accionable breve (máximo 2 líneas)
2. Una explicación concisa de por qué se generó esta alerta (máximo 2 líneas)

Formato de respuesta:
RECOMENDACIÓN: [tu recomendación]
EXPLICACIÓN: [tu explicación]
"""
        
        try:
            response = httpx.post(
                f"{self.base_url}/models/gemini-pro:generateContent?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_ai_response(text)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
        
        # Fallback si falla la API
        return self._get_fallback_recommendation(
            piso, variable, nivel, valor_actual, umbral
        )
    
    def _parse_ai_response(self, text: str) -> Tuple[str, str]:
        """Parsea la respuesta de la IA"""
        lines = text.strip().split("\n")
        recomendacion = ""
        explicacion = ""
        
        for line in lines:
            if line.startswith("RECOMENDACIÓN:"):
                recomendacion = line.replace("RECOMENDACIÓN:", "").strip()
            elif line.startswith("EXPLICACIÓN:"):
                explicacion = line.replace("EXPLICACIÓN:", "").strip()
        
        if not recomendacion:
            recomendacion = "Revisar condiciones del piso y ajustar parámetros según sea necesario."
        if not explicacion:
            explicacion = "Alerta generada por exceder umbrales configurados."
        
        return recomendacion, explicacion
    
    def _get_fallback_recommendation(
        self,
        piso: int,
        variable: str,
        nivel: str,
        valor_actual: float,
        umbral: float
    ) -> Tuple[str, str]:
        """Recomendaciones predefinidas cuando no hay API key"""
        
        recomendaciones = {
            "temperatura": {
                "critica": f"Ajustar temperatura del Piso {piso} a 24°C en los próximos 15 min. Verificar sistema HVAC.",
                "media": f"Monitorear temperatura del Piso {piso}. Considerar ajuste gradual del sistema de climatización.",
                "informativa": f"Temperatura del Piso {piso} ligeramente elevada. Mantener monitoreo."
            },
            "humedad": {
                "critica": f"Acción inmediata requerida en Piso {piso}. Ajustar sistema de humidificación/deshumidificación.",
                "media": f"Monitorear humedad del Piso {piso}. Verificar sistema de control ambiental.",
                "informativa": f"Humedad del Piso {piso} fuera del rango óptimo. Observar tendencias."
            },
            "energia": {
                "critica": f"Consumo energético crítico en Piso {piso}. Revisar equipos y optimizar carga.",
                "media": f"Consumo elevado en Piso {piso}. Identificar equipos de alto consumo.",
                "informativa": f"Consumo energético del Piso {piso} por encima del promedio. Revisar patrones."
            }
        }
        
        explicaciones = {
            "temperatura": f"Temperatura ({valor_actual}°C) supera umbral {nivel} ({umbral}°C).",
            "humedad": f"Humedad ({valor_actual}%) fuera del rango {nivel} (umbral: {umbral}%).",
            "energia": f"Consumo energético ({valor_actual} kW) excede umbral {nivel} ({umbral} kW)."
        }
        
        recomendacion = recomendaciones.get(variable, {}).get(nivel, "Revisar condiciones del piso.")
        explicacion = explicaciones.get(variable, f"Variable {variable} excede umbral configurado.")
        
        return recomendacion, explicacion

