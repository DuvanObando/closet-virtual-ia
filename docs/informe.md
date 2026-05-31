# 📄 Informe Técnico — Closet Virtual con IA

**Proyecto:** Sistema Experto de Recomendación de Outfits
**Autor:** Duvan Obando
**Asignatura:** Sistemas Expertos con IA
**Fecha:** Mayo 2026
**Repositorio:** https://github.com/DuvanObando/closet-virtual-ia

---

## 1. Introducción

Los sistemas expertos son programas de inteligencia artificial que emulan el razonamiento de un especialista humano en un dominio específico mediante reglas de inferencia formales. Tradicionalmente se han aplicado a diagnóstico médico, soporte técnico o evaluación financiera. Este proyecto explora su aplicación en un dominio cotidiano y visual: la **recomendación de outfits**.

El sistema desarrollado integra un motor clásico de reglas (forward chaining) con un modelo de lenguaje multimodal (Google Gemini 2.5 Flash) capaz de analizar imágenes de prendas reales subidas por el usuario. La combinación permite obtener lo mejor de dos paradigmas: la explicabilidad y rigor del razonamiento simbólico, junto con la flexibilidad y comprensión visual del aprendizaje profundo.

## 2. Objetivos

**Objetivo general:** Diseñar e implementar un sistema experto funcional que recomiende combinaciones de prendas (outfits) a partir de imágenes reales y del contexto del usuario, utilizando APIs gratuitas de IA.

**Objetivos específicos:**

- Implementar una arquitectura abstraída que permita cambiar de proveedor de IA (Gemini, Groq) sin modificar el código del dominio.
- Diseñar al menos 20 reglas de inferencia categorizadas que cubran composición, estilo, color, temporada y género.
- Integrar análisis multimodal de imágenes para extraer atributos estructurados (tipo, color, estilo, patrón) en formato JSON.
- Construir un dashboard interactivo con Streamlit que muestre el flujo completo: hechos iniciales, hechos derivados, reglas activadas y recomendación final.
- Publicar el proyecto en un repositorio público con documentación reproducible.

## 3. Marco teórico

### 3.1 Sistemas expertos

Un sistema experto se compone clásicamente de tres elementos: una **base de conocimiento** (hechos y reglas), un **motor de inferencia** que aplica las reglas, y una **interfaz de usuario** que recoge consultas y muestra resultados. El razonamiento puede ser hacia adelante (forward chaining), partiendo de los hechos para llegar a conclusiones, o hacia atrás (backward chaining), partiendo de una hipótesis y buscando hechos que la sustenten.

### 3.2 Forward chaining

El algoritmo de encadenamiento hacia adelante implementado funciona así:

1. Recibe un conjunto de hechos iniciales `F` y un conjunto de reglas `R`.
2. Para cada regla `r ∈ R`, si todas sus condiciones están en `F` y su conclusión aún no está, añade la conclusión a `F` y registra la regla como activada.
3. Repite hasta que ninguna regla nueva pueda dispararse (convergencia).

### 3.3 Modelos de lenguaje multimodales

Los modelos como Gemini 2.5 Flash o Llama 4 Scout pueden procesar texto e imagen de forma conjunta. En este proyecto se aprovecha esa capacidad para que el LLM actúe como un "extractor de atributos visuales", devolviendo un JSON estructurado que se conecta directamente al motor simbólico de reglas.

## 4. Arquitectura del sistema

El sistema sigue una arquitectura en capas:

    ┌─────────────────────────────────────────────┐
    │  app.py  (Streamlit Dashboard)              │
    │  - Captura de prendas y contexto            │
    │  - Visualización de hechos y reglas         │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │  utils/image_processor.py                   │
    │  - Llama al agente para extraer JSON        │
    │  - Sanea la respuesta del LLM               │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │  agents/base_agent_universal.py             │
    │  - ExpertAgent (Gemini | Groq | auto)       │
    │  - analyze_image / query_agent / forward_chain
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │  rules/reglas_outfits.py                    │
    │  - 21 reglas de inferencia                  │
    │  - prenda_a_hechos / contexto_a_hechos      │
    └─────────────────────────────────────────────┘

La separación en capas permite por ejemplo añadir un proveedor nuevo (Ollama, HuggingFace) editando solamente `base_agent_universal.py`, sin tocar reglas ni dashboard.

## 5. Implementación

### 5.1 Stack tecnológico

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.14 |
| Dashboard | Streamlit 1.57 |
| IA multimodal | Google Gemini 2.5 Flash (vía SDK `google-genai` 2.4) |
| Respaldo | Groq (Llama 4 Scout / Llama 3.3 70B) |
| Gestión secretos | python-dotenv |
| Imágenes | Pillow |
| Control de versiones | Git + GitHub |
| Entorno | WSL2 (Ubuntu) sobre Windows 11 |

### 5.2 Reglas implementadas

Se diseñaron **21 reglas** distribuidas en 6 categorías:

| Categoría | Reglas | Ejemplo |
|-----------|--------|---------|
| Composición | R01-R02 | superior + inferior + calzado → outfit completo |
| Formal | R03-R05 | camisa + pantalón + calzado formal → ejecutivo |
| Casual | R06-R10 | camisa + jean + tenis → smart casual |
| Deportivo | R11-R12 | estilo deportivo + leggings + tenis → outfit fitness |
| Color | R13-R16 | base neutra + color vivo → contraste balanceado |
| Temporada | R17-R19 | abrigo + verano → alerta abrigo excesivo |
| Género | R20-R21 | vestido + masculino → alerta incompatibilidad |

### 5.3 Diseño de hechos abstractos

Una decisión clave fue generar **hechos abstractos** además de los específicos durante la conversión `prenda → hechos`. Por ejemplo, una camisa azul casual lisa genera:

    prenda:camisa
    tiene:superior
    tiene:superior_formal
    color:azul
    color:vivo
    estilo:casual
    patron:liso

Esto permite que una regla genérica como R01 (`tiene:superior + tiene:inferior + tiene:calzado → outfit:completo`) se dispare con cualquier combinación, en vez de necesitar una regla específica para cada par (camisa+pantalón, polo+jean, blusa+falda, etc.).

### 5.4 Extracción de atributos con Gemini

Se construyó un prompt estructurado que fuerza al modelo a devolver exclusivamente JSON, con campos predefinidos y valores enumerados (tipo, color, estilo, patrón, temporada, material). Una función de saneamiento (`_extraer_json`) elimina bloques markdown opcionales y extrae el objeto JSON aunque venga acompañado de texto adicional, aumentando la robustez del parseo.

## 6. Pruebas y resultados

### 6.1 Caso de prueba documentado

**Entrada:**

- 3 prendas: camisa gris con estampado geométrico, jean azul, tenis rojos.
- Contexto: masculino, ocasión casual, temporada verano.

**Resultados del motor:**

- 23 hechos iniciales generados.
- 3 hechos derivados: `outfit:base_armada`, `outfit:completo`, `outfit:smart_casual`.
- 6 reglas activadas: R01, R02, R07, R13, R14, R15.

**Recomendación de Gemini (extracto):**

> "Este conjunto es perfecto para tu ocasión casual y la temporada de verano. El jean azul y los tenis rojos forman una base cómoda y relajada (...) La camisa gris con patrón geométrico eleva el look de forma sutil, dándole un toque moderno y chic que encaja muy bien con el estilo smart casual."

Las capturas del flujo completo se encuentran en `docs/capturas/`.

### 6.2 Verificación de cobertura de reglas

Cada categoría de reglas se probó al menos una vez. Las reglas de alerta (R19, R20) se validaron con casos artificiales (sueter en verano, vestido en masculino) ejecutando `python3 -m rules.reglas_outfits` con datos sintéticos.

## 7. Decisiones técnicas relevantes

- **Gemini como proveedor principal** por su soporte multimodal nativo de alta calidad y cuota gratis amplia (1M tokens/día).
- **Groq como respaldo** automático mediante detección de variables de entorno en el constructor del agente.
- **SDK `google-genai`** en lugar del deprecado `google-generativeai`, alineándose con la versión GA actual.
- **WSL2** elegido sobre PowerShell para facilitar el uso de Streamlit y comandos Unix.

Detalle completo en `docs/decisiones_tecnicas.md`.

## 8. Problemas encontrados y soluciones

- **Bug del prefijo `AQ.` en claves de Gemini (mayo 2026):** Google AI Studio comenzó a emitir claves con prefijo `AQ.` en lugar del clásico `AIzaSy`, y algunas eran rechazadas por la API con error `401 ACCESS_TOKEN_TYPE_UNSUPPORTED`. Solución: regenerar la clave en AI Studio hasta obtener una funcional.
- **Reglas iniciales demasiado estrictas:** las primeras reglas exigían coincidencia exacta del tipo de prenda (`prenda:camiseta`), fallando cuando el modelo identificaba `camisa`. Se rediseñaron usando hechos abstractos (`tiene:superior`).
- **Python 3.14 muy reciente:** algunos paquetes requirieron compilación. No hubo fallos, pero las dependencias se instalaron más lento de lo habitual.

## 9. Limitaciones

- El sistema depende de la calidad de extracción del LLM: si la imagen es ambigua, los atributos pueden ser incorrectos.
- No hay persistencia: las prendas se pierden al cerrar la sesión de Streamlit.
- Las reglas son estáticas; un sistema más avanzado podría aprender combinaciones nuevas a partir del feedback del usuario.
- El catálogo de tipos de prendas es fijo (16 tipos); prendas exóticas pueden no encajar.

## 10. Trabajo futuro

- Persistencia con SQLite o JSON local para guardar el closet entre sesiones.
- Sistema de feedback (usuario marca outfits como "me gusta" / "no me gusta") para refinar prioridades.
- Soporte para accesorios (corbatas, sombreros, joyería).
- Reglas con probabilidad/peso, no solo binarias.
- Despliegue público en Streamlit Cloud o Hugging Face Spaces.

## 11. Conclusiones

El proyecto demuestra que es viable combinar un sistema experto clásico con un LLM multimodal moderno, aprovechando la explicabilidad de las reglas y la capacidad de comprensión visual del modelo. La arquitectura modular permite cambiar de proveedor de IA fácilmente, y el flujo end-to-end (foto → atributos → hechos → reglas → recomendación) funciona correctamente con prendas reales en menos de 30 segundos.

Las 21 reglas implementadas cubren los escenarios principales de combinación de outfits, y el dashboard de Streamlit hace transparente el razonamiento del sistema, mostrando al usuario qué hechos se dedujeron y qué reglas se activaron. Esto cumple uno de los principios clásicos de los sistemas expertos: la **explicabilidad**.

## 12. Referencias

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4ª ed.). Capítulos sobre Knowledge-Based Agents y Forward/Backward Chaining.
- Google AI for Developers — Gemini API documentation: https://ai.google.dev/gemini-api/docs
- Streamlit documentation: https://docs.streamlit.io
- Groq Cloud documentation: https://console.groq.com/docs
