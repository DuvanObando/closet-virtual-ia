# 👔 Closet Virtual - Sistema Experto con IA

Sistema experto de recomendación de outfits que combina **reglas de inferencia** (forward chaining) con **análisis multimodal de imágenes** mediante la API gratuita de Google Gemini.

## 🎯 Descripción

El usuario sube fotos de sus prendas reales, indica su contexto (género, ocasión, temporada), y el sistema:

1. Extrae atributos de cada prenda usando Gemini 2.5 Flash (multimodal).
2. Convierte las prendas en hechos (prenda:camisa, color:azul, tiene:calzado_casual, etc.).
3. Aplica un motor de inferencia con 21 reglas categorizadas (formal, casual, deportivo, color, temporada, género).
4. Genera una recomendación personalizada en lenguaje natural usando el LLM.

## 🛠️ Stack tecnológico

- Python 3.10+ (probado en 3.14)
- Streamlit — dashboard interactivo
- google-genai — SDK oficial de Gemini
- python-dotenv — gestión de variables de entorno
- Motor de reglas propio con forward chaining

## 📂 Estructura del proyecto

    closet-virtual-ia/
    ├── app.py                        # Dashboard Streamlit
    ├── agents/
    │   └── base_agent_universal.py   # Clase ExpertAgent (Gemini + Groq)
    ├── rules/
    │   └── reglas_outfits.py         # 21 reglas + motor auxiliar
    ├── utils/
    │   └── image_processor.py        # Extracción de atributos desde imagen
    ├── data/test/                    # Imágenes de prueba
    ├── docs/                         # Informe y decisiones técnicas
    ├── requirements.txt
    ├── .env.example
    └── .gitignore

## 🚀 Instalación

1. Clonar el repositorio:

       git clone <url-del-repo>
       cd closet-virtual-ia

2. Crear y activar entorno virtual:

       python3 -m venv venv
       source venv/bin/activate

3. Instalar dependencias:

       pip install -r requirements.txt

4. Configurar API key de Gemini:

       cp .env.example .env
       # Editar .env y añadir tu GEMINI_API_KEY de https://aistudio.google.com/apikey

5. Ejecutar el dashboard:

       streamlit run app.py

Abrir el navegador en http://localhost:8501

## 🧪 Uso

1. Configurar género, ocasión y temporada en la parte superior.
2. Subir 3 a 10 fotos de prendas reales.
3. Pulsar "🔍 Analizar prendas" (Gemini extrae los atributos).
4. Pulsar "✨ Generar outfit recomendado" para ver hechos, reglas activadas y recomendación.

## 📋 Reglas del sistema experto

21 reglas en 6 categorías:

- Composición (R01-R02): superior + inferior + calzado → outfit completo
- Formal (R03-R05): camisa + pantalón + calzado formal → ejecutivo
- Casual (R06-R10): camisa + jean + tenis → smart casual
- Deportivo (R11-R12): leggings + tenis + estilo deportivo → outfit fitness
- Color (R13-R16): base neutra + color vivo → contraste balanceado
- Temporada (R17-R19): sueter en verano → alerta abrigo excesivo
- Género (R20-R21): vestido + masculino → alerta incompatibilidad

## 🔬 Decisiones técnicas

- Proveedor: Gemini 2.5 Flash (1M tokens/día gratis, multimodal).
- Arquitectura abstraída: ExpertAgent permite cambiar a Groq sin tocar el código.
- Forward chaining: encadenamiento hacia adelante hasta convergencia.
- Hechos abstractos: además de "prenda:camisa", se generan "tiene:superior" para reglas flexibles.

Ver docs/decisiones_tecnicas.md para más detalle.

## 👤 Autor

Duvan Obando — Sistemas Expertos con IA
