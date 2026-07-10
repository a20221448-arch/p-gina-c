import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Trivia: ¿Mito o realidad sobre el SOMP?",
    page_icon="🩺",
    layout="centered"
)

# ---------------------------------------------------------
# Nombre del archivo de datos (debe estar en el mismo repo,
# junto a este app.py)
# ---------------------------------------------------------
NOMBRE_ARCHIVO = "Pensamiento - Base de datos.xlsx"

# ---------------------------------------------------------
# Cargar la base de datos (cacheada para no releerla en cada
# interacción del usuario)
# ---------------------------------------------------------
@st.cache_data
def cargar_datos(ruta):
    df = pd.read_excel(ruta)
    return df


def archivo_existe(ruta):
    return os.path.exists(ruta)


st.title("🩺💜 Trivia: ¿Mito o realidad sobre el SOMP?")
st.write("Pon a prueba tus conocimientos y combate la desinformación.")

if not archivo_existe(NOMBRE_ARCHIVO):
    st.error(
        f"❌ No se encontró el archivo **{NOMBRE_ARCHIVO}** en el repositorio.\n\n"
        "Asegúrate de que el archivo esté subido en GitHub, en la misma carpeta "
        "que `app.py`, y que el nombre coincida exactamente (incluyendo mayúsculas "
        "y espacios)."
    )
    st.stop()

df = cargar_datos(NOMBRE_ARCHIVO)

# ---------------------------------------------------------
# Validar columnas requeridas
# ---------------------------------------------------------
columnas_requeridas = [
    "nivel",
    "categoría",
    "mito",
    "A",
    "B",
    "C",
    "D",
    "respuesta",
    "explicación"
]

faltantes = [c for c in columnas_requeridas if c not in df.columns]

if faltantes:
    st.error(f"❌ Faltan estas columnas en el Excel: {', '.join(faltantes)}")
    st.stop()

# ---------------------------------------------------------
# Inicializar el estado del juego
# ---------------------------------------------------------
if "etapa" not in st.session_state:
    st.session_state.etapa = "seleccion_nivel"   # seleccion_nivel -> jugando -> resultado
    st.session_state.nivel_elegido = None
    st.session_state.preguntas = None
    st.session_state.indice = 0
    st.session_state.puntaje = 0
    st.session_state.respondido = False
    st.session_state.ultima_correcta = None
    st.session_state.ultima_explicacion = None
    st.session_state.ultima_respuesta_correcta = None


def reiniciar_juego():
    st.session_state.etapa = "seleccion_nivel"
    st.session_state.nivel_elegido = None
    st.session_state.preguntas = None
    st.session_state.indice = 0
    st.session_state.puntaje = 0
    st.session_state.respondido = False
    st.session_state.ultima_correcta = None
    st.session_state.ultima_explicacion = None
    st.session_state.ultima_respuesta_correcta = None


# ---------------------------------------------------------
# ETAPA 1: Selección de nivel
# ---------------------------------------------------------
if st.session_state.etapa == "seleccion_nivel":

    orden_niveles = ["Fácil", "Medio", "Difícil"]
    niveles_disponibles = [n for n in orden_niveles if n in df["nivel"].unique()]

    st.subheader("📚 Elige un nivel")

    nivel_elegido = st.radio(
        "Niveles disponibles:",
        niveles_disponibles,
        index=None
    )

    if st.button("Comenzar", type="primary", disabled=(nivel_elegido is None)):
        preguntas_nivel = df[df["nivel"] == nivel_elegido]

        if len(preguntas_nivel) == 0:
            st.error("❌ No existen preguntas para ese nivel.")
        else:
            cantidad = min(10, len(preguntas_nivel))
            preguntas = preguntas_nivel.sample(n=cantidad, random_state=None).reset_index(drop=True)

            st.session_state.nivel_elegido = nivel_elegido
            st.session_state.preguntas = preguntas
            st.session_state.indice = 0
            st.session_state.puntaje = 0
            st.session_state.respondido = False
            st.session_state.etapa = "jugando"
            st.rerun()

# ---------------------------------------------------------
# ETAPA 2: Jugando
# ---------------------------------------------------------
elif st.session_state.etapa == "jugando":

    preguntas = st.session_state.preguntas
    cantidad_preguntas = len(preguntas)
    numero = st.session_state.indice + 1

    if st.session_state.indice >= cantidad_preguntas:
        st.session_state.etapa = "resultado"
        st.rerun()

    fila = preguntas.iloc[st.session_state.indice]

    st.progress(st.session_state.indice / cantidad_preguntas)
    st.caption(f"📖 Pregunta {numero} de {cantidad_preguntas} · Nivel: {st.session_state.nivel_elegido}")
    st.caption(f"📂 Categoría: {fila['categoría']}")

    st.markdown("### 🔷 MITO")
    st.write(fila["mito"])

    opciones = {
        "A": fila["A"],
        "B": fila["B"],
        "C": fila["C"],
        "D": fila["D"],
    }

    if not st.session_state.respondido:
        etiqueta_elegida = st.radio(
            "Tu respuesta:",
            list(opciones.keys()),
            format_func=lambda k: f"{k}) {opciones[k]}",
            index=None,
            key=f"respuesta_{st.session_state.indice}"
        )

        if st.button("Confirmar respuesta", type="primary", disabled=(etiqueta_elegida is None)):
            correcta = str(fila["respuesta"]).strip().upper()
            es_correcta = etiqueta_elegida == correcta

            if es_correcta:
                st.session_state.puntaje += 1

            st.session_state.respondido = True
            st.session_state.ultima_correcta = es_correcta
            st.session_state.ultima_respuesta_correcta = correcta
            st.session_state.ultima_explicacion = fila["explicación"]
            st.rerun()

    else:
        if st.session_state.ultima_correcta:
            st.success("✅ ¡Correcto!")
        else:
            st.error(f"❌ Incorrecto. Respuesta correcta: {st.session_state.ultima_respuesta_correcta}")

        st.info(f"💡 {st.session_state.ultima_explicacion}")

        texto_boton = "Siguiente pregunta" if numero < cantidad_preguntas else "Ver resultados"

        if st.button(texto_boton, type="primary"):
            st.session_state.indice += 1
            st.session_state.respondido = False
            st.rerun()

# ---------------------------------------------------------
# ETAPA 3: Resultado final
# ---------------------------------------------------------
elif st.session_state.etapa == "resultado":

    cantidad_preguntas = len(st.session_state.preguntas)
    puntaje = st.session_state.puntaje
    porcentaje = (puntaje / cantidad_preguntas) * 100

    st.header("🏁 FIN DEL JUEGO")
    st.subheader(f"➡️ Puntaje: {puntaje}/{cantidad_preguntas}")

    if porcentaje == 100:
        st.success("🏆 ¡Excelente! Conoces muy bien el SOMP.")
    elif porcentaje >= 80:
        st.success("🌟 Muy buen trabajo. Tienes conocimientos sólidos sobre el SOMP.")
    elif porcentaje >= 60:
        st.info("👏 Vas por buen camino. Sigue aprendiendo sobre el SOMP.")
    elif porcentaje >= 40:
        st.warning("👀 Aún existen algunos mitos por aclarar.")
    else:
        st.warning("📖 Sigue informándote sobre el SOMP y ayuda a combatir la desinformación.")

    st.write("💜 Gracias por jugar y aprender sobre el SOMP.")

    if st.button("🔁 Jugar de nuevo"):
        reiniciar_juego()
        st.rerun()
