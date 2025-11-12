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
    
    def _calculate_temperature_target(self, valor_actual: float, nivel: str) -> float:
        """Calcula la temperatura objetivo según el nivel de alerta"""
        # Temperatura óptima: 24°C (estándar de confort)
        TEMP_OPTIMA = 24.0
        
        if nivel == "critica":
            # Crítica: >= 29.5°C -> objetivo: 24°C (acción inmediata)
            return TEMP_OPTIMA
        elif nivel == "media":
            # Media: 28-29.4°C -> objetivo: 24-25°C (volver a rango óptimo)
            # Si está muy alta, reducir más agresivamente
            if valor_actual >= 29.0:
                return TEMP_OPTIMA
            else:
                return 25.0
        elif nivel == "informativa":
            # Informativa: 26-27.9°C -> objetivo: 25°C (un poco por debajo del umbral)
            return 25.0
        else:
            return TEMP_OPTIMA
    
    def _calculate_humidity_target(self, valor_actual: float, nivel: str) -> float:
        """Calcula la humedad objetivo según el nivel de alerta"""
        # Humedad óptima: 50-60% (centro: 55%)
        HUMEDAD_OPTIMA = 55.0
        
        # Siempre apuntar al centro del rango óptimo
        return HUMEDAD_OPTIMA
    
    def _get_fallback_recommendation(
        self,
        piso: int,
        variable: str,
        nivel: str,
        valor_actual: float,
        umbral: float
    ) -> Tuple[str, str]:
        """Recomendaciones predefinidas cuando no hay API key"""
        
        if variable == "temperatura":
            temp_target = self._calculate_temperature_target(valor_actual, nivel)
            
            if nivel == "critica":
                recomendacion = (
                    f"Ajustar temperatura del Piso {piso} a {temp_target}°C en los próximos 15 min. "
                    f"Verificar sistema HVAC y asegurar enfriamiento inmediato."
                )
            elif nivel == "media":
                recomendacion = (
                    f"Reducir temperatura del Piso {piso} gradualmente a {temp_target}°C. "
                    f"Monitorear cada 30 min hasta estabilizar en rango óptimo."
                )
            else:  # informativa
                recomendacion = (
                    f"Optimizar temperatura del Piso {piso} hacia {temp_target}°C. "
                    f"Temperatura actual ({valor_actual}°C) ligeramente elevada."
                )
            
            explicacion = (
                f"Temperatura actual: {valor_actual}°C. "
                f"Umbral {nivel}: {'≥29.5°C' if nivel == 'critica' else '28-29.4°C' if nivel == 'media' else '26-27.9°C'}. "
                f"Objetivo: {temp_target}°C (rango óptimo: 24°C)."
            )
            
        elif variable == "humedad":
            humedad_target = self._calculate_humidity_target(valor_actual, nivel)
            
            # Determinar si está alta o baja
            es_baja = valor_actual < 50
            
            if nivel == "critica":
                if es_baja:
                    recomendacion = (
                        f"Acción inmediata: aumentar humedad del Piso {piso} a {humedad_target}%. "
                        f"Valor actual ({valor_actual}%) críticamente bajo (<20%)."
                    )
                else:
                    recomendacion = (
                        f"Acción inmediata: reducir humedad del Piso {piso} a {humedad_target}%. "
                        f"Valor actual ({valor_actual}%) críticamente alto (>80%)."
                    )
            elif nivel == "media":
                if es_baja:
                    recomendacion = (
                        f"Ajustar humedad del Piso {piso} hacia {humedad_target}%. "
                        f"Valor actual ({valor_actual}%) muy bajo (<22%). Verificar sistema de humidificación."
                    )
                else:
                    recomendacion = (
                        f"Ajustar humedad del Piso {piso} hacia {humedad_target}%. "
                        f"Valor actual ({valor_actual}%) muy alto (>75%). Verificar sistema de deshumidificación."
                    )
            else:  # informativa
                if es_baja:
                    recomendacion = (
                        f"Monitorear humedad del Piso {piso}. Valor actual ({valor_actual}%) por debajo del óptimo. "
                        f"Objetivo: {humedad_target}%."
                    )
                else:
                    recomendacion = (
                        f"Monitorear humedad del Piso {piso}. Valor actual ({valor_actual}%) por encima del óptimo. "
                        f"Objetivo: {humedad_target}%."
                    )
            
            rango_umbral = "<20% o >80%" if nivel == "critica" else "<22% o >75%" if nivel == "media" else "<25% o >70%"
            explicacion = (
                f"Humedad actual: {valor_actual}%. "
                f"Umbral {nivel}: {rango_umbral}. "
                f"Objetivo: {humedad_target}% (rango óptimo: 50-60%)."
            )
            
        elif variable == "energia":
            if nivel == "critica":
                recomendacion = (
                    f"Consumo energético crítico en Piso {piso} ({valor_actual} kW). "
                    f"Revisar inmediatamente equipos de alto consumo y optimizar carga operativa."
                )
            elif nivel == "media":
                recomendacion = (
                    f"Consumo elevado en Piso {piso} ({valor_actual} kW). "
                    f"Identificar circuitos de mayor demanda y redistribuir carga si es posible."
                )
            else:  # informativa
                recomendacion = (
                    f"Consumo energético del Piso {piso} ({valor_actual} kW) por encima del promedio. "
                    f"Revisar patrones de uso y programaciones de equipos."
                )
            
            explicacion = (
                f"Consumo actual: {valor_actual} kW. "
                f"Umbral {nivel}: {'≥25 kW' if nivel == 'critica' else '20-25 kW' if nivel == 'media' else '15-20 kW'}. "
                f"Revisar equipos y optimizar eficiencia energética."
            )
        else:
            recomendacion = f"Revisar condiciones del Piso {piso} para la variable {variable}."
            explicacion = f"Variable {variable} excede umbral configurado ({umbral})."
        
        return recomendacion, explicacion

