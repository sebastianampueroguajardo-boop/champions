import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64 as bs64
import re

df = pd.read_csv("champs.csv")

st.markdown("""
<style>
* { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("Champions League 2014/2015")


def fondo(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = bs64.b64encode(data).decode()

    css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

fondo("UEFA.webp")


def fondo_sidebar(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = bs64.b64encode(data).decode()

    css = f"""
    <style>
    [data-testid="stSidebar"] > div:first-child {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    return css

st.markdown(fondo_sidebar("blue.jpg"), unsafe_allow_html=True)

def split_goals(x):
    if isinstance(x, str):
        x = re.sub(r"[^\d\-]", "", x)
        if "-" in x:
            try:
                a, b = x.split("-")
                return int(a), int(b)
            except:
                return None, None
    return None, None

df["g1"], df["g2"] = zip(*df["FT"].apply(split_goals))
df["total_goals"] = df["g1"] + df["g2"]

def get_year(x):
    if isinstance(x, str):
        for part in x.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
    return None

df["year"] = df["Date"].apply(get_year)


with st.sidebar:
    st.header("Opciones")

    years = ["Todos"] + sorted(df["year"].dropna().unique())
    selected_year = st.selectbox("Selecciona el año:", years)

    bins = st.slider("Número de bins para histograma:", 1, 20, 10)

    mostrar_tabla = st.radio("Mostrar tabla completa:", ["No", "Sí"])





filtered = df.copy()
if selected_year != "Todos":
    filtered = filtered[filtered["year"] == selected_year]

tab1, tab2, tab3, tab4 = st.tabs(["Estadísticas Generales", "Goles y Equipos", "Fases y Países", "Dataset"])


with tab1:
    st.subheader("Gráficos generales")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].hist(filtered["total_goals"].dropna(), bins=bins)
    ax[0].set_title("Histograma de goles")

    partidos_por_año = df.groupby("year")["FT"].count()
    ax[1].bar(partidos_por_año.index, partidos_por_año.values)
    ax[1].set_title("Partidos por año")

    st.pyplot(fig)


with tab2:
    st.subheader("Gráficos de goles y equipos")

    g1 = df.groupby("Team 1")["g1"].sum()
    g2 = df.groupby("Team 2")["g2"].sum()
    g_total = g1.add(g2, fill_value=0).sort_values(ascending=False).head(10)

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(g_total.index, g_total.values)
    ax2.set_xticklabels(g_total.index, rotation=90)
    st.pyplot(fig2)

  
    todos = pd.concat([df["Team 1"], df["Team 2"]])
    nombres = todos.str.split(" › ").str[0]

    st.write("### Equipos con más partidos")

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    top_mas = nombres.value_counts().head(10)
    ax3.bar(top_mas.index, top_mas.values)
    ax3.set_xticklabels(top_mas.index, rotation=90)
    st.pyplot(fig3)


with tab3:
    st.subheader("Fases del torneo y países")

    fases = df["Stage"].value_counts()
    fig4, ax4 = plt.subplots(figsize=(7, 7))
    ax4.pie(fases.values, labels=fases.index, autopct="%1.1f%%")
    ax4.set_title("Partidos por fase")
    st.pyplot(fig4)

    tabla_split = todos.str.split(" › ", expand=True)
    equipos = tabla_split[0]
    paises_raw = tabla_split[1]
    paises_limpios = paises_raw.str.split(" \(").str[0]
    datos = pd.DataFrame({"Equipo": equipos, "Pais": paises_limpios}).drop_duplicates()
    conteo_paises = datos["Pais"].value_counts().head(10)

    fig5, ax5 = plt.subplots(figsize=(10, 4))
    ax5.bar(conteo_paises.index, conteo_paises.values)
    ax5.set_xticklabels(conteo_paises.index, rotation=90)
    st.pyplot(fig5)


with tab4:
    st.subheader("Vista de datos")

    if mostrar_tabla == "Sí":
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Se muestra una vista previa del dataset (primeras 10 filas):")
        st.dataframe(df.head(10), use_container_width=True)

    st.write("## 🏆 Campeón del torneo")

    if st.button("Mostrar campeón"):

        final = df.tail(1).iloc[0]

        
        equipo1 = final["Team 1"].split(" › ")[0]
        equipo2 = final["Team 2"].split(" › ")[0]

        goles1 = int(final["FT"].split("-")[0])
        goles2 = int(final["FT"].split("-")[1])

        campeon = equipo1 if goles1 > goles2 else equipo2

        st.write(f"### Campeón: **{campeon}**")

        ruta = "barcelona_escudo.png"

        try:
            st.image(ruta, width=200)
        except:
            st.error("No se pudo cargar el escudo del campeón.")

        st.write("### Datos de la final:")
        st.dataframe(df.tail(1), use_container_width=True)

