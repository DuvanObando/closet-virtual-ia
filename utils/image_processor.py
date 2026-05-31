"""
Procesador de imágenes para el sistema experto Closet Virtual.
Usa el ExpertAgent para extraer atributos estructurados de prendas
desde imágenes subidas por el usuario.
"""
import json
import re
from agents.base_agent_universal import ExpertAgent


# ----------------------------------------------------------------------
# PROMPT DE EXTRACCIÓN DE ATRIBUTOS
# ----------------------------------------------------------------------
PROMPT_ANALISIS_PRENDA = """Analiza la prenda de ropa en la imagen y devuelve EXCLUSIVAMENTE un objeto JSON válido con esta estructura exacta (sin texto adicional, sin markdown, solo el JSON):

{
  "tipo": "<uno de: camisa, camiseta, polo, blusa, sueter, chaqueta, blazer, vestido, pantalon, jean, short, falda, leggings, zapatos_formales, tenis, sandalias, botas, tacones, mocasines>",
  "categoria": "<uno de: superior, inferior, calzado, accesorio>",
  "color": "<color predominante: negro, blanco, gris, beige, crema, marron, rojo, naranja, amarillo, rosa, coral, azul, verde, morado, celeste, turquesa>",
  "color_secundario": "<color secundario o 'ninguno'>",
  "estilo": "<uno de: formal, casual, deportivo, elegante>",
  "patron": "<uno de: liso, rayas, cuadros, estampado, floral, geometrico>",
  "temporada": "<uno de: verano, invierno, primavera, otonio, todo_ano>",
  "material_aparente": "<algodon, lino, lana, mezclilla, cuero, sintetico, desconocido>",
  "descripcion_corta": "<descripción breve de 5-10 palabras de la prenda>"
}

Si no puedes identificar algún campo con seguridad, usa el valor más probable. NO incluyas explicaciones, NO uses bloques de código markdown (```), responde SOLO con el JSON."""


# ----------------------------------------------------------------------
# CLASE PROCESADORA
# ----------------------------------------------------------------------
class ImageProcessor:
    """
    Encapsula la lógica de análisis de imágenes para extraer prendas.
    """

    def __init__(self, agent: ExpertAgent = None):
        """
        agent: instancia opcional de ExpertAgent.
        Si no se pasa, se crea uno con detección automática.
        """
        self.agent = agent or ExpertAgent(provider="auto")

    def analizar_prenda(self, image_bytes: bytes) -> dict:
        """
        Analiza una imagen de prenda y devuelve un dict con sus atributos.
        Si el modelo no devuelve JSON válido, retorna un dict con 'error'.
        """
        raw_response = self.agent.analyze_image(
            image_bytes=image_bytes,
            prompt=PROMPT_ANALISIS_PRENDA,
        )

        # Limpieza: a veces el modelo devuelve markdown ```json ... ```
        cleaned = self._extraer_json(raw_response)

        try:
            atributos = json.loads(cleaned)
            atributos["_raw"] = raw_response  # guardamos respuesta original por trazabilidad
            return atributos
        except json.JSONDecodeError as e:
            return {
                "error": "El modelo no devolvió JSON válido",
                "detalle": str(e),
                "_raw": raw_response,
            }

    def analizar_lote(self, imagenes: list) -> list:
        """
        Analiza una lista de imágenes (bytes) y devuelve lista de atributos.
        imagenes: [(nombre_archivo, bytes), ...]
        """
        resultados = []
        for nombre, img_bytes in imagenes:
            atributos = self.analizar_prenda(img_bytes)
            atributos["archivo"] = nombre
            resultados.append(atributos)
        return resultados

    @staticmethod
    def _extraer_json(texto: str) -> str:
        """
        Limpia la respuesta del modelo para obtener solo el JSON.
        Maneja casos donde el modelo envuelve la respuesta en ```json ... ```
        o agrega texto antes/después.
        """
        # Quitar bloques de código markdown
        texto = re.sub(r"^```(?:json)?\s*", "", texto.strip())
        texto = re.sub(r"\s*```$", "", texto.strip())

        # Buscar el primer { hasta el último } por si hay texto extra
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return match.group(0)
        return texto


# ----------------------------------------------------------------------
# Bloque de prueba (requiere una imagen real para probar)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Uso: python3 utils/image_processor.py <ruta_a_imagen.jpg>")
        print("Ejemplo: python3 utils/image_processor.py data/test_camisa.jpg")
        sys.exit(1)

    ruta = sys.argv[1]
    if not os.path.exists(ruta):
        print(f"ERROR: archivo no encontrado: {ruta}")
        sys.exit(1)

    print(f"Analizando: {ruta}\n")
    with open(ruta, "rb") as f:
        img_bytes = f.read()

    processor = ImageProcessor()
    resultado = processor.analizar_prenda(img_bytes)

    print("=== ATRIBUTOS EXTRAÍDOS ===")
    for clave, valor in resultado.items():
        if clave != "_raw":
            print(f"  {clave}: {valor}")

    if "error" in resultado:
        print("\n=== RESPUESTA CRUDA DEL MODELO ===")
        print(resultado["_raw"])
