# 📐 Decisiones técnicas

## 1. Elección del proveedor de IA

Se compararon las 4 alternativas gratuitas propuestas (Groq, Gemini, Ollama, HuggingFace).

| Criterio | Groq | Gemini | Ollama | HuggingFace |
|----------|------|--------|--------|-------------|
| Multimodal (imagen) | Parcial (Llama 4 Scout) | Nativo | Limitado | Variable |
| Cuota gratis | 14,400 req/día | 1M tokens/día | Ilimitado | 1,000 req/día |
| Requiere tarjeta | No | No | No | No |
| Velocidad | Muy alta | Alta | Baja (CPU) | Media |
| Hardware local | No | No | 8GB+ RAM | No |

Decisión: Gemini 2.5 Flash como proveedor principal por su soporte nativo multimodal de alta calidad, indispensable para clasificar prendas desde fotos. Groq queda como respaldo en base_agent_universal.py para soportar fallback automático.

## 2. Arquitectura del agente

Se implementó la clase ExpertAgent (agents/base_agent_universal.py) con tres métodos:

- analyze_image(image_bytes, prompt) — envía imagen + instrucción al LLM multimodal.
- query_agent(system_prompt, message) — consulta de texto con system prompt.
- forward_chain(facts, rules) — motor de inferencia con encadenamiento hacia adelante.

El constructor detecta automáticamente el proveedor disponible según las variables de entorno (GEMINI_API_KEY → GROQ_API_KEY).

## 3. Diseño del sistema de reglas

Se eligió forward chaining clásico: parte de un conjunto de hechos iniciales y aplica reglas iterativamente hasta que no se generen nuevos hechos.

Para que las reglas sean flexibles y reutilizables, además de hechos específicos (prenda:camisa) se generan hechos abstractos durante la conversión:

- prenda:camisa → genera también tiene:superior y tiene:superior_formal
- prenda:tenis → genera también tiene:calzado y tiene:calzado_casual
- color:azul → genera también color:vivo

Esto permite que una regla como R01 (tiene:superior + tiene:inferior + tiene:calzado → outfit:completo) funcione con cualquier combinación de prendas, no solo con tipos hardcodeados.

## 4. Extracción de atributos desde imagen

Se utiliza un prompt estructurado que fuerza al LLM a devolver JSON con campos predefinidos: tipo, categoria, color, color_secundario, estilo, patron, temporada, material_aparente.

Una función _extraer_json() limpia la respuesta del modelo (elimina bloques markdown y captura solo el objeto JSON válido), aumentando la robustez ante variaciones en el formato de respuesta.

## 5. Seguridad y manejo de claves

- La clave API se guarda en .env (excluido por .gitignore).
- .env.example se incluye con placeholders para guiar a otros desarrolladores.
- El SDK google-genai reemplazó al deprecado google-generativeai (este último mostraba FutureWarning y dejará de funcionar).

## 6. Problemas encontrados

- Bug del prefijo AQ. en las claves de Gemini (mayo 2026): Google AI Studio comenzó a emitir claves con prefijo AQ. en lugar del clásico AIzaSy. Algunas de estas claves son rechazadas por el endpoint v1beta con error 401 ACCESS_TOKEN_TYPE_UNSUPPORTED. La solución fue regenerar la clave hasta obtener una válida.
- Coincidencia exacta vs. flexible en reglas: las primeras versiones de las reglas eran demasiado estrictas (exigían prenda:camiseta literal y fallaban con prenda:camisa). Se rediseñaron usando hechos abstractos.
