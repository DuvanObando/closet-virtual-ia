"""
Agente universal para el sistema experto Closet Virtual.
Abstrae el proveedor de IA (Gemini como principal, Groq como respaldo).
"""
import os
import base64
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


class ExpertAgent:
    """
    Agente experto que combina:
    - Análisis multimodal de imágenes (extracción de atributos de prendas)
    - Generación de texto con system prompt (recomendaciones de outfits)
    - Motor de inferencia con encadenamiento hacia adelante (forward chaining)
    """

    def __init__(self, provider: str = "auto"):
        """
        Inicializa el agente con el proveedor especificado.
        provider: "gemini", "groq" o "auto" (detecta el disponible)
        """
        self.provider = self._detect_provider(provider)
        self.client = self._init_client()
        print(f"[ExpertAgent] Proveedor activo: {self.provider}")

    def _detect_provider(self, provider: str) -> str:
        """Detecta el proveedor disponible según las variables de entorno."""
        if provider == "auto":
            if os.getenv("GEMINI_API_KEY"):
                return "gemini"
            elif os.getenv("GROQ_API_KEY"):
                return "groq"
            else:
                raise ValueError(
                    "No se encontró ninguna API key. "
                    "Configura GEMINI_API_KEY o GROQ_API_KEY en el archivo .env"
                )
        return provider

    def _init_client(self):
        """Instancia el cliente del proveedor seleccionado."""
        if self.provider == "gemini":
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY no encontrada en .env")
            return genai.Client(api_key=api_key)

        elif self.provider == "groq":
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY no encontrada en .env")
            return Groq(api_key=api_key)

        else:
            raise ValueError(f"Proveedor no soportado: {self.provider}")

    # ------------------------------------------------------------------
    # MÉTODO 1: Análisis de imágenes (multimodal)
    # ------------------------------------------------------------------
    def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """
        Envía una imagen al modelo y devuelve la descripción textual.
        image_bytes: contenido binario de la imagen (PNG/JPG)
        prompt: instrucción de qué extraer de la imagen
        """
        if self.provider == "gemini":
            from google.genai import types
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
            )
            return response.text

        elif self.provider == "groq":
            # Groq usa formato OpenAI con imagen en base64
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    }
                ],
            )
            return response.choices[0].message.content

    # ------------------------------------------------------------------
    # MÉTODO 2: Consulta de texto con system prompt
    # ------------------------------------------------------------------
    def query_agent(self, system_prompt: str, user_message: str) -> str:
        """
        Envía un mensaje de texto al modelo con un system prompt definido.
        Útil para generar explicaciones de outfits, justificaciones, etc.
        Responde siempre en español.
        """
        system_prompt_es = system_prompt + "\n\nResponde siempre en español."

        if self.provider == "gemini":
            from google.genai import types
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt_es
                ),
            )
            return response.text

        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt_es},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content

    # ------------------------------------------------------------------
    # MÉTODO 3: Motor de inferencia (forward chaining)
    # ------------------------------------------------------------------
    def forward_chain(self, facts: set, rules: list) -> tuple:
        """
        Aplica encadenamiento hacia adelante sobre un conjunto de hechos.
        facts: conjunto de hechos iniciales (set de strings)
        rules: lista de dicts {'id', 'cond' (lista/set), 'conclusion'}
        Devuelve: (hechos_finales, reglas_activadas)
        """
        facts = set(facts)
        fired_rules = []
        changed = True

        while changed:
            changed = False
            for rule in rules:
                conditions = set(rule["cond"])
                if conditions.issubset(facts) and rule["conclusion"] not in facts:
                    facts.add(rule["conclusion"])
                    fired_rules.append(rule["id"])
                    changed = True

        return facts, fired_rules


# ----------------------------------------------------------------------
# Bloque de prueba rápida (se ejecuta solo si corres el archivo directo)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    agent = ExpertAgent(provider="auto")

    # Prueba 1: consulta de texto
    print("\n--- PRUEBA 1: query_agent ---")
    resp = agent.query_agent(
        system_prompt="Eres un asistente de moda experto en outfits.",
        user_message="Dame una idea breve de outfit casual de verano para hombre.",
    )
    print(resp)

    # Prueba 2: forward chaining con reglas dummy
    print("\n--- PRUEBA 2: forward_chain ---")
    hechos = {"camisa_formal", "pantalon_vestir", "zapatos_formales"}
    reglas = [
        {
            "id": "R1",
            "cond": ["camisa_formal", "pantalon_vestir"],
            "conclusion": "estilo_formal_parcial",
        },
        {
            "id": "R2",
            "cond": ["estilo_formal_parcial", "zapatos_formales"],
            "conclusion": "outfit_formal_completo",
        },
    ]
    facts_final, fired = agent.forward_chain(hechos, reglas)
    print(f"Hechos finales: {facts_final}")
    print(f"Reglas activadas: {fired}")
