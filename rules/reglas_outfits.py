"""
Reglas del sistema experto para recomendación de outfits.
"""

# ----------------------------------------------------------------------
# CATÁLOGOS
# ----------------------------------------------------------------------
PRENDAS_SUPERIORES = ["camisa", "camiseta", "polo", "blusa", "sueter", "chaqueta", "blazer", "vestido"]
PRENDAS_INFERIORES = ["pantalon", "jean", "short", "falda", "leggings"]
CALZADOS = ["zapatos_formales", "tenis", "sandalias", "botas", "tacones", "mocasines"]
ACCESORIOS = ["corbata", "cinturon", "bufanda", "gorra", "sombrero", "reloj"]

COLORES_NEUTROS = ["negro", "blanco", "gris", "beige", "crema", "marron"]
COLORES_CALIDOS = ["rojo", "naranja", "amarillo", "rosa", "coral"]
COLORES_FRIOS = ["azul", "verde", "morado", "celeste", "turquesa"]

OCASIONES = ["oficina", "casual", "deportiva", "elegante", "playa", "fiesta", "cita"]
TEMPORADAS = ["verano", "invierno", "primavera", "otonio"]
GENEROS = ["masculino", "femenino", "unisex"]

# Calzados formales vs casuales (para reglas más flexibles)
CALZADOS_FORMALES = ["zapatos_formales", "tacones", "mocasines"]
CALZADOS_CASUALES = ["tenis", "sandalias"]


# ----------------------------------------------------------------------
# REGLAS DE INFERENCIA
# ----------------------------------------------------------------------
REGLAS_OUTFITS = [
    # === REGLAS DE COMPOSICIÓN BÁSICA ===
    {
        "id": "R01",
        "descripcion": "Hay prenda superior + inferior + calzado → outfit completo",
        "cond": ["tiene:superior", "tiene:inferior", "tiene:calzado"],
        "conclusion": "outfit:completo",
        "categoria": "composicion",
    },
    {
        "id": "R02",
        "descripcion": "Solo prenda superior + inferior (sin calzado) → outfit incompleto",
        "cond": ["tiene:superior", "tiene:inferior"],
        "conclusion": "outfit:base_armada",
        "categoria": "composicion",
    },

    # === REGLAS DE ESTILO FORMAL ===
    {
        "id": "R03",
        "descripcion": "Camisa o blazer + pantalón + calzado formal → estilo ejecutivo",
        "cond": ["tiene:superior_formal", "tiene:pantalon", "tiene:calzado_formal"],
        "conclusion": "outfit:ejecutivo",
        "categoria": "formal",
    },
    {
        "id": "R04",
        "descripcion": "Vestido + tacones (femenino) → outfit elegante femenino",
        "cond": ["prenda:vestido", "calzado:tacones", "genero:femenino"],
        "conclusion": "outfit:elegante_femenino",
        "categoria": "formal",
    },
    {
        "id": "R05",
        "descripcion": "Outfit ejecutivo + ocasión oficina → recomendado para oficina",
        "cond": ["outfit:ejecutivo", "ocasion:oficina"],
        "conclusion": "recomendacion:apto_oficina",
        "categoria": "formal",
    },

    # === REGLAS DE ESTILO CASUAL ===
    {
        "id": "R06",
        "descripcion": "Prenda superior casual + jean o short + tenis → outfit casual",
        "cond": ["tiene:superior_casual", "tiene:inferior_casual", "calzado:tenis"],
        "conclusion": "outfit:casual_basico",
        "categoria": "casual",
    },
    {
        "id": "R07",
        "descripcion": "Camisa + jean + tenis → smart casual",
        "cond": ["prenda:camisa", "prenda:jean", "calzado:tenis"],
        "conclusion": "outfit:smart_casual",
        "categoria": "casual",
    },
    {
        "id": "R08",
        "descripcion": "Polo + pantalón + mocasines → smart casual masculino",
        "cond": ["prenda:polo", "prenda:pantalon", "calzado:mocasines"],
        "conclusion": "outfit:smart_casual",
        "categoria": "casual",
    },
    {
        "id": "R09",
        "descripcion": "Outfit smart casual + ocasión cita → recomendado para cita",
        "cond": ["outfit:smart_casual", "ocasion:cita"],
        "conclusion": "recomendacion:apto_cita",
        "categoria": "casual",
    },
    {
        "id": "R10",
        "descripcion": "Outfit casual + ocasión casual → recomendado",
        "cond": ["outfit:casual_basico", "ocasion:casual"],
        "conclusion": "recomendacion:apto_casual",
        "categoria": "casual",
    },

    # === REGLAS DE ESTILO DEPORTIVO ===
    {
        "id": "R11",
        "descripcion": "Estilo deportivo + short o leggings + tenis → outfit deportivo",
        "cond": ["estilo:deportivo", "tiene:inferior_deportivo", "calzado:tenis"],
        "conclusion": "outfit:deportivo",
        "categoria": "deportivo",
    },
    {
        "id": "R12",
        "descripcion": "Outfit deportivo + ocasión deportiva → apto para gimnasio",
        "cond": ["outfit:deportivo", "ocasion:deportiva"],
        "conclusion": "recomendacion:apto_gimnasio",
        "categoria": "deportivo",
    },

    # === REGLAS DE ARMONÍA DE COLOR ===
    {
        "id": "R13",
        "descripcion": "Hay al menos una prenda con color neutro → base segura",
        "cond": ["color:neutro"],
        "conclusion": "armonia:base_neutra",
        "categoria": "color",
    },
    {
        "id": "R14",
        "descripcion": "Base neutra + color vivo → contraste balanceado",
        "cond": ["armonia:base_neutra", "color:vivo"],
        "conclusion": "armonia:contraste_balanceado",
        "categoria": "color",
    },
    {
        "id": "R15",
        "descripcion": "Hay al menos un patrón → atención a combinaciones",
        "cond": ["patron:con_patron"],
        "conclusion": "estilo:con_estampado",
        "categoria": "color",
    },
    {
        "id": "R16",
        "descripcion": "Estampado + más de un color vivo → alerta de sobrecarga visual",
        "cond": ["estilo:con_estampado", "color:vivo", "color:adicional_vivo"],
        "conclusion": "alerta:sobrecarga_visual",
        "categoria": "color",
    },

    # === REGLAS DE TEMPORADA ===
    {
        "id": "R17",
        "descripcion": "Hay sueter o chaqueta → apto para invierno",
        "cond": ["tiene:abrigo"],
        "conclusion": "temporada:invierno_apto",
        "categoria": "temporada",
    },
    {
        "id": "R18",
        "descripcion": "Hay short o sandalias → apto para verano",
        "cond": ["tiene:fresco"],
        "conclusion": "temporada:verano_apto",
        "categoria": "temporada",
    },
    {
        "id": "R19",
        "descripcion": "Abrigo + temporada verano → alerta abrigo excesivo",
        "cond": ["tiene:abrigo", "temporada:verano"],
        "conclusion": "alerta:abrigo_excesivo",
        "categoria": "temporada",
    },

    # === REGLAS DE GÉNERO ===
    {
        "id": "R20",
        "descripcion": "Vestido + género masculino → alerta de incompatibilidad",
        "cond": ["prenda:vestido", "genero:masculino"],
        "conclusion": "alerta:prenda_incompatible_genero",
        "categoria": "genero",
    },
    {
        "id": "R21",
        "descripcion": "Corbata + género femenino → estilo andrógino",
        "cond": ["prenda:corbata", "genero:femenino"],
        "conclusion": "estilo:androgino",
        "categoria": "genero",
    },
]


# ----------------------------------------------------------------------
# FUNCIONES AUXILIARES (versión mejorada)
# ----------------------------------------------------------------------
def get_reglas_por_categoria(categoria: str) -> list:
    return [r for r in REGLAS_OUTFITS if r["categoria"] == categoria]


def get_regla_por_id(rule_id: str) -> dict:
    for r in REGLAS_OUTFITS:
        if r["id"] == rule_id:
            return r
    return None


def prenda_a_hechos(prenda: dict) -> set:
    """
    Convierte una prenda en hechos. Genera tanto hechos específicos
    (prenda:camisa) como hechos abstractos (tiene:superior, tiene:calzado)
    para que las reglas sean más flexibles.
    """
    hechos = set()
    tipo = prenda.get("tipo", "").lower()
    color = prenda.get("color", "").lower()
    estilo = prenda.get("estilo", "").lower()
    patron = prenda.get("patron", "").lower()

    # --- Hecho específico de tipo de prenda ---
    if tipo:
        hechos.add(f"prenda:{tipo}")

        # --- Hechos abstractos por categoría ---
        if tipo in PRENDAS_SUPERIORES:
            hechos.add("tiene:superior")
            if tipo in ["camisa", "blazer", "blusa"]:
                hechos.add("tiene:superior_formal")
            if tipo in ["camiseta", "polo", "vestido"]:
                hechos.add("tiene:superior_casual")
            if tipo in ["sueter", "chaqueta", "blazer"]:
                hechos.add("tiene:abrigo")

        if tipo in PRENDAS_INFERIORES:
            hechos.add("tiene:inferior")
            if tipo == "pantalon":
                hechos.add("tiene:pantalon")
            if tipo in ["jean", "short"]:
                hechos.add("tiene:inferior_casual")
            if tipo in ["short", "leggings"]:
                hechos.add("tiene:inferior_deportivo")
            if tipo == "short":
                hechos.add("tiene:fresco")

        if tipo in CALZADOS:
            hechos.add("tiene:calzado")
            hechos.add(f"calzado:{tipo}")
            if tipo in CALZADOS_FORMALES:
                hechos.add("tiene:calzado_formal")
            if tipo in CALZADOS_CASUALES:
                hechos.add("tiene:calzado_casual")
            if tipo == "sandalias":
                hechos.add("tiene:fresco")

    # --- Color ---
    if color:
        hechos.add(f"color:{color}")
        if color in COLORES_NEUTROS:
            hechos.add("color:neutro")
        elif color in COLORES_CALIDOS or color in COLORES_FRIOS:
            hechos.add("color:vivo")

    # --- Estilo ---
    if estilo:
        hechos.add(f"estilo:{estilo}")

    # --- Patrón ---
    if patron:
        if patron == "liso":
            hechos.add("patron:liso")
        else:
            hechos.add("patron:con_patron")

    return hechos


def contexto_a_hechos(genero: str, ocasion: str, temporada: str) -> set:
    hechos = set()
    if genero:
        hechos.add(f"genero:{genero}")
    if ocasion:
        hechos.add(f"ocasion:{ocasion}")
    if temporada:
        hechos.add(f"temporada:{temporada}")
    return hechos


# ----------------------------------------------------------------------
# Prueba
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Total de reglas: {len(REGLAS_OUTFITS)}")

    # Caso de prueba: camisa azul + jean azul + tenis rojos, contexto casual/verano
    from agents.base_agent_universal import ExpertAgent

    prendas = [
        {"tipo": "camisa", "color": "azul", "estilo": "casual", "patron": "liso"},
        {"tipo": "jean", "color": "azul", "estilo": "casual", "patron": "liso"},
        {"tipo": "tenis", "color": "rojo", "estilo": "deportivo", "patron": "liso"},
    ]

    hechos = set()
    hechos |= contexto_a_hechos("masculino", "casual", "verano")
    for p in prendas:
        hechos |= prenda_a_hechos(p)

    print(f"\nHechos iniciales ({len(hechos)}):")
    for h in sorted(hechos):
        print(f"  - {h}")

    agent = ExpertAgent(provider="auto")
    finales, fired = agent.forward_chain(hechos, REGLAS_OUTFITS)
    nuevos = finales - hechos

    print(f"\nHechos derivados ({len(nuevos)}):")
    for h in sorted(nuevos):
        print(f"  + {h}")

    print(f"\nReglas activadas: {fired}")
