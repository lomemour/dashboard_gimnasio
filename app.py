"""Dashboard del gimnasio. Lee SOLO los CSV exportados de gimnasio_db (carpeta datos/)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROSA, ROSA_CLARO, NEGRO, BLANCO, FONDO = "#FF1493", "#FFC0CB", "#2C2C2C", "#FFFFFF", "#FFF5F7"
FUENTE = "Poppins, Quicksand, sans-serif"
DATOS = Path(__file__).parent / "datos"
MESES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
NOMBRE_METODO = {"app": "App", "QR": "Código QR", "recepcion": "Recepción"}
ORDEN_PLAN = ["Básico", "Plus", "Premium"]
ORDEN_EDAD = ["<30", "30-49", "50+"]

st.set_page_config(page_title="Gimnasio · Dashboard", page_icon="🏋️", layout="wide")
st.markdown(f"""<style>
.stApp, [data-testid="stHeader"] {{ background: {FONDO}; }}
.stApp p, .stApp span, .stApp label, .stApp li,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"] {{ color: {NEGRO} !important; }}
h1, h2, h3 {{ color: {ROSA} !important; }}
</style>""", unsafe_allow_html=True)


def estilo(fig, titulo):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=20, color=ROSA)),
        font=dict(family=FUENTE, size=14, color=NEGRO),
        plot_bgcolor=BLANCO, paper_bgcolor=FONDO,
        margin=dict(l=40, r=40, t=70, b=40), legend_title_text="",
    )
    return fig


@st.cache_data
def cargar(nombre):
    ruta = DATOS / nombre
    return pd.read_csv(ruta) if ruta.exists() else None


mes_disc = cargar("asistencias_mes_disciplina.csv")
plan = cargar("comportamiento_plan.csv")
canal = cargar("canal_edad.csv")

st.title("🏋️ Asistencia en la cadena de gimnasios")
st.caption("Fuente: consultas SQL sobre gimnasio_db, sesiones realizadas. "
           "Los datos son sintéticos, sembrados por el equipo para probar el modelo.")

faltan = [n for n, d in [("asistencias_mes_disciplina.csv", mes_disc),
                         ("comportamiento_plan.csv", plan), ("canal_edad.csv", canal)] if d is None]
if faltan:
    st.error("Faltan archivos en la carpeta `datos/`: " + ", ".join(faltan) +
             ". Expórtalos con las consultas de `consultas_exportar.sql`.")
    st.stop()

# ---------- 1. Estacionalidad ----------
mes = mes_disc.groupby("mes", as_index=False)["asistencias"].sum().sort_values("mes")
mes["etiqueta"] = mes["mes"].map(lambda m: MESES[int(m[5:7])] + (f" {m[:4]}" if m[5:7] in ("01",) else ""))
pico, valle = mes.loc[mes["asistencias"].idxmax()], mes.loc[mes["asistencias"].idxmin()]

c1, c2, c3 = st.columns(3)
c1.metric("Asistencias totales", f"{int(mes['asistencias'].sum()):,}".replace(",", "."))
c2.metric(f"Pico · {pico['etiqueta']}", f"{int(pico['asistencias']):,}".replace(",", "."))
c3.metric(f"Valle · {valle['etiqueta']}", f"{int(valle['asistencias']):,}".replace(",", "."))

fig1 = px.area(mes, x="etiqueta", y="asistencias", markers=True, color_discrete_sequence=[ROSA_CLARO])
fig1.update_traces(line=dict(color=ROSA, width=4), marker=dict(size=10, color=ROSA))
for fila, txt, ay in [(pico, "Pico", -40), (valle, "Valle", 40)]:
    fig1.add_annotation(x=fila["etiqueta"], y=fila["asistencias"], ay=ay, showarrow=True,
                        text=f"{txt}: {int(fila['asistencias']):,}".replace(",", "."), arrowcolor=NEGRO)
fig1.update_xaxes(title="", categoryorder="array", categoryarray=list(mes["etiqueta"]))
fig1.update_yaxes(title="Asistencias", rangemode="tozero", gridcolor="#EFEFEF")
st.plotly_chart(estilo(fig1, "1. Asistencias por mes"), width="stretch", theme=None)

# ---------- 2. Carrera por disciplina ----------
top = mes_disc.groupby("disciplina")["asistencias"].sum().nlargest(10).index
cum = mes_disc[mes_disc["disciplina"].isin(top)].sort_values("mes").copy()
cum["acumulado"] = cum.groupby("disciplina")["asistencias"].cumsum()
cum["etiqueta"] = cum["mes"].map(lambda m: MESES[int(m[5:7])] + " " + m[:4])
orden = list(dict.fromkeys(cum["etiqueta"]))
fig2 = px.bar(cum, x="acumulado", y="disciplina", color="disciplina", animation_frame="etiqueta",
              animation_group="disciplina", range_x=[0, cum["acumulado"].max() * 1.15],
              category_orders={"etiqueta": orden},
              color_discrete_sequence=[ROSA, NEGRO, ROSA_CLARO, "#FF8DA1", "#8B0A50", "#B0B0B0", "#C2185B", "#6D6D6D", "#F48FB1", "#AD1457"])
fig2.update_xaxes(title="Asistencias acumuladas")
fig2.update_yaxes(title="")
st.plotly_chart(estilo(fig2, "2. Asistencia acumulada · 10 disciplinas con más asistencia (botón Play)"), width="stretch", theme=None)

# ---------- 3. Plan: frecuencia y puntualidad ----------
plan["plan"] = pd.Categorical(plan["plan"], [p for p in ORDEN_PLAN if p in set(plan["plan"])], ordered=True)
plan = plan.sort_values("plan")
colores = {"Básico": ROSA_CLARO, "Plus": "#FF8DA1", "Premium": ROSA}
colA, colB = st.columns(2)
fa = px.bar(plan, x="plan", y="visitas_por_socio", color="plan", text="visitas_por_socio",
            color_discrete_map=colores)
fa.update_traces(textposition="outside"); fa.update_xaxes(title=""); fa.update_yaxes(title="Visitas por socio")
colA.plotly_chart(estilo(fa, "3a. Visitas por socio según plan"), width="stretch", theme=None)
fb = px.bar(plan, x="plan", y="minutos_anticipacion", color="plan", text="minutos_anticipacion",
            color_discrete_map=colores)
fb.update_traces(textposition="outside"); fb.update_xaxes(title="")
fb.update_yaxes(title="Minutos de anticipación (negativo = tarde)", zeroline=True, zerolinecolor=NEGRO)
colB.plotly_chart(estilo(fb, "3b. Puntualidad según plan"), width="stretch", theme=None)
st.caption("Socios por plan: " + " · ".join(f"{r.plan}: {int(r.socios)}" for r in plan.itertuples()))

# ---------- 4. Canal de ingreso por edad ----------
canal["metodo"] = canal["metodo"].map(NOMBRE_METODO).fillna(canal["metodo"])
canal["pct"] = canal["usos"] / canal.groupby("rango_edad")["usos"].transform("sum") * 100
fig4 = px.bar(canal, x="rango_edad", y="pct", color="metodo", barmode="stack",
              text=canal["pct"].round(0).astype(int).astype(str) + "%",
              category_orders={"rango_edad": ORDEN_EDAD},
              color_discrete_map={"App": ROSA, "Código QR": NEGRO, "Recepción": ROSA_CLARO})
fig4.update_xaxes(title="Rango de edad"); fig4.update_yaxes(title="% de los ingresos", range=[0, 100])
st.plotly_chart(estilo(fig4, "4. Canal de ingreso según edad"), width="stretch", theme=None)
