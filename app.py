"""
Closet Virtual - Sistema Experto de Recomendación de Outfits
Dashboard principal con Streamlit.
"""
import streamlit as st
import pandas as pd
from io import BytesIO

from agents.base_agent_universal import ExpertAgent
from utils.image_processor import ImageProcessor
from rules.reglas_outfits import (
    REGLAS_OUTFITS,
    prenda_a_hechos,
    contexto_a_hechos,
    OCASIONES,
    TEMPORADAS,
    GENEROS,
)


# ----------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Closet Virtual - Sistema Experto",
    page_icon="👔",
    layout="wide",
)


# ----------------------------------------------------------------------
# INICIALIZACIÓN DEL AGENTE (con caché para no reinstanciarlo)
# ----------------------------------------------------------------------
@st.cache_resource
def get_agent():
    return ExpertAgent(provider="auto")


@st.cache_resource
def get_processor(_agent):
    return ImageProcessor(agent=_agent)


# ----------------------------------------------------------------------
# ESTADO DE SESIÓN
# ----------------------------------------------------------------------
if "prendas_analizadas" not in st.session_state:
    st.session_state.prendas_analizadas = []
if "outfit_actual" not in st.session_state:
    st.session_state.outfit_actual = None


# ----------------------------------------------------------------------
# BARRA LATERAL
# ----------------------------------------------------------------------
st.sidebar.title("👔 Closet Virtual")
st.sidebar.markdown("**Sistema Experto de Outfits**")

try:
    agent = get_agent()
    processor = get_processor(agent)
    st.sidebar.success(f"✅ Proveedor activo: **{agent.provider}**")
except Exception as e:
    st.sidebar.error(f"❌ Error inicializando agente:\n\n{e}")
    st.stop()

st.sidebar.divider()
st.sidebar.markdown("### 📋 Reglas cargadas")
st.sidebar.metric("Total de reglas", len(REGLAS_OUTFITS))

with st.sidebar.expander("Ver categorías"):
    categorias = pd.Series([r["categoria"] for r in REGLAS_OUTFITS]).value_counts()
    st.bar_chart(categorias)

st.sidebar.divider()
if st.sidebar.button("🗑️ Limpiar closet"):
    st.session_state.prendas_analizadas = []
    st.session_state.outfit_actual = None
    st.rerun()


# ----------------------------------------------------------------------
# TÍTULO PRINCIPAL
# ----------------------------------------------------------------------
st.title("👔 Closet Virtual con IA")
st.markdown(
    "Sube fotos de tus prendas, indica la ocasión y deja que el sistema experto "
    "te recomiende el mejor outfit usando reglas de inferencia + Gemini."
)


# ----------------------------------------------------------------------
# PASO 1: CONTEXTO DEL USUARIO
# ----------------------------------------------------------------------
st.header("1️⃣ Configura tu contexto")
col_g, col_o, col_t = st.columns(3)

with col_g:
    genero = st.selectbox("Género", GENEROS, index=2)
with col_o:
    ocasion = st.selectbox("Ocasión", OCASIONES, index=1)
with col_t:
    temporada = st.selectbox("Temporada", TEMPORADAS, index=0)


# ----------------------------------------------------------------------
# PASO 2: SUBIR PRENDAS
# ----------------------------------------------------------------------
st.header("2️⃣ Sube tus prendas (3 a 10 fotos)")
archivos = st.file_uploader(
    "Selecciona imágenes de tus prendas",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

col_a, col_b = st.columns([1, 3])
with col_a:
    analizar_btn = st.button(
        "🔍 Analizar prendas",
        type="primary",
        disabled=not archivos,
    )
with col_b:
    if archivos:
        st.caption(f"📁 {len(archivos)} imagen(es) seleccionada(s)")

if analizar_btn and archivos:
    st.session_state.prendas_analizadas = []
    progress = st.progress(0, text="Iniciando análisis...")
    for i, archivo in enumerate(archivos):
        progress.progress(
            (i + 1) / len(archivos),
            text=f"Analizando {archivo.name} ({i + 1}/{len(archivos)})...",
        )
        img_bytes = archivo.read()
        atributos = processor.analizar_prenda(img_bytes)
        atributos["archivo"] = archivo.name
        atributos["imagen_bytes"] = img_bytes
        st.session_state.prendas_analizadas.append(atributos)
    progress.empty()
    st.success(f"✅ {len(archivos)} prenda(s) analizada(s) correctamente.")


# ----------------------------------------------------------------------
# PASO 3: MOSTRAR PRENDAS ANALIZADAS
# ----------------------------------------------------------------------
if st.session_state.prendas_analizadas:
    st.header("3️⃣ Prendas en tu closet")

    cols = st.columns(min(4, len(st.session_state.prendas_analizadas)))
    for i, prenda in enumerate(st.session_state.prendas_analizadas):
        with cols[i % len(cols)]:
            if "imagen_bytes" in prenda:
                st.image(prenda["imagen_bytes"], use_container_width=True)
            if "error" in prenda:
                st.error(f"❌ {prenda['archivo']}: {prenda['error']}")
            else:
                st.markdown(f"**{prenda.get('tipo', '?').title()}**")
                st.caption(
                    f"🎨 {prenda.get('color', '?')} · "
                    f"✨ {prenda.get('estilo', '?')} · "
                    f"🔳 {prenda.get('patron', '?')}"
                )
                with st.expander("Ver detalles"):
                    detalles = {k: v for k, v in prenda.items()
                                if k not in ("imagen_bytes", "_raw", "archivo")}
                    st.json(detalles)


# ----------------------------------------------------------------------
# PASO 4: MOTOR DE INFERENCIA Y RECOMENDACIÓN
# ----------------------------------------------------------------------
if st.session_state.prendas_analizadas:
    st.header("4️⃣ Generar recomendación de outfit")

    if st.button("✨ Generar outfit recomendado", type="primary"):

        # ---- Construir hechos iniciales ----
        hechos = set()
        hechos |= contexto_a_hechos(genero, ocasion, temporada)
        for prenda in st.session_state.prendas_analizadas:
            if "error" not in prenda:
                hechos |= prenda_a_hechos(prenda)

        # ---- Ejecutar forward chaining ----
        hechos_finales, reglas_activadas = agent.forward_chain(hechos, REGLAS_OUTFITS)
        nuevos_hechos = hechos_finales - hechos

        # ---- Mostrar resultados del motor ----
        col_h, col_r = st.columns(2)
        with col_h:
            st.subheader("📌 Hechos iniciales")
            st.write(sorted(hechos))
            if nuevos_hechos:
                st.subheader("🆕 Hechos derivados")
                st.write(sorted(nuevos_hechos))
            else:
                st.info("No se derivaron hechos nuevos. Prueba con más prendas.")
        with col_r:
            st.subheader("⚙️ Reglas activadas")
            if reglas_activadas:
                for rid in reglas_activadas:
                    regla = next(r for r in REGLAS_OUTFITS if r["id"] == rid)
                    st.markdown(f"**{rid}** — {regla['descripcion']}")
            else:
                st.warning("Ninguna regla se activó con la combinación actual.")

        # ---- Generar explicación con Gemini ----
        st.subheader("👗 Recomendación personalizada")
        with st.spinner("Generando recomendación con IA..."):
            prendas_texto = "\n".join([
                f"- {p.get('tipo', '?')} {p.get('color', '?')} "
                f"({p.get('estilo', '?')}, {p.get('patron', '?')})"
                for p in st.session_state.prendas_analizadas
                if "error" not in p
            ])

            outfits_detectados = [h for h in hechos_finales if h.startswith("outfit:")]
            alertas = [h for h in hechos_finales if h.startswith("alerta:")]

            system_prompt = (
                "Eres un estilista profesional. Recibes un listado de prendas, "
                "el contexto del usuario, los outfits válidos detectados por un motor "
                "de reglas y posibles alertas. Tu tarea es proponer UNA combinación "
                "concreta usando las prendas listadas, explicar por qué funciona "
                "(armonía de color, ocasión, temporada), y mencionar si hay alertas "
                "a tener en cuenta. Sé claro, breve y amigable."
            )

            mensaje = f"""
**Contexto del usuario:**
- Género: {genero}
- Ocasión: {ocasion}
- Temporada: {temporada}

**Prendas disponibles:**
{prendas_texto}

**Outfits válidos detectados por el motor de reglas:**
{outfits_detectados if outfits_detectados else "Ninguno detectado automáticamente."}

**Alertas:**
{alertas if alertas else "Sin alertas."}

Propón el mejor outfit posible y explica por qué.
"""
            try:
                recomendacion = agent.query_agent(system_prompt, mensaje)
                st.markdown(recomendacion)
                st.session_state.outfit_actual = recomendacion
            except Exception as e:
                st.error(f"Error generando recomendación: {e}")


# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
st.divider()
st.caption(
    "🎓 Sistema Experto Closet Virtual · Proveedor: "
    f"{agent.provider} · "
    f"{len(REGLAS_OUTFITS)} reglas activas"
)
