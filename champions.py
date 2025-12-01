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
    st.subheader("en el histograma se muestra la cantidad de partidos que tuvieron cierta cantidad de goles")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].hist(filtered["total_goals"].dropna(), bins=bins)
    ax[0].set_title("Histograma de goles")

    partidos_por_año = df.groupby("year")["FT"].count()
    ax[1].bar(partidos_por_año.index, partidos_por_año.values)
    ax[1].set_title("Partidos por año")
    
    ax[1].set_xticks(partidos_por_año.index)
    ax[1].set_xticklabels(partidos_por_año.index, rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig)


with tab2:
    st.subheader("Equipos con menos partidos jugados")

    todos = pd.concat([df['Team 1'], df['Team 2']])
    nombres = todos.str.split(' › ').str[0]
    top_menos_equipos = nombres.value_counts().tail(10)

    fig_menos, ax_menos = plt.subplots(figsize=(10, 5))
    ax_menos.bar(top_menos_equipos.index, top_menos_equipos.values)
    ax_menos.set_title("Equipos con menos partidos jugados")
    ax_menos.set_ylabel("Partidos jugados")
    ax_menos.set_xticklabels(top_menos_equipos.index, rotation=90)

    st.pyplot(fig_menos)
    
    st.write("### Equipos con más partidos")

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    top_mas = nombres.value_counts().head(10)
    ax3.bar(top_mas.index, top_mas.values)
    ax3.set_xticklabels(top_mas.index, rotation=90)
    ax3.set_title("equipos con mas partidos jugados")
    st.pyplot(fig3)


    st.subheader("Variación de goles por cada fase")

    goles = df['FT'].str.split(' ').str[0].str.split('-', expand=True).astype(int)
    df['Goles'] = goles[0] + goles[1]

    df['Fase'] = df['Stage']
    filtro = df['Stage'] == 'Knockout'
    df.loc[filtro, 'Fase'] = df.loc[filtro, 'Round'].str.split('|').str[0].str.strip()

    datos = df.groupby('Fase')['Goles'].sum()

    orden = ['Qualifying', 'Group', 'Round of 16', 'Quarterfinals', 'Semifinals', 'Final']
    datos = datos.reindex(orden)

    fig_linea, ax_linea = plt.subplots(figsize=(10, 6))
    ax_linea.plot(datos.index, datos.values, marker='o')
    ax_linea.set_title("Variación de goles por cada fase")
    ax_linea.set_ylabel("Goles")
    ax_linea.grid(True)

    st.pyplot(fig_linea)
    
    st.subheader("Equipos con más goles")

    df["Team1_clean"] = df["Team 1"].str.split(" › ").str[0]
    df["Team2_clean"] = df["Team 2"].str.split(" › ").str[0]

    g1 = df.groupby("Team1_clean")["g1"].sum()
    g2 = df.groupby("Team2_clean")["g2"].sum()

    goles_total = g1.add(g2, fill_value=0).sort_values(ascending=False).head(10)

    fig_goles, ax_goles = plt.subplots(figsize=(10, 5))
    ax_goles.barh(range(len(goles_total)), goles_total.values)

    ax_goles.set_yticks(range(len(goles_total)))
    ax_goles.set_yticklabels(goles_total.index)

    ax_goles.set_title("Top 10 equipos con más goles")
    ax_goles.set_xlabel("Goles")

    st.pyplot(fig_goles)
 



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
    ax5.set_title("equipos por pais")
    st.pyplot(fig5)


with tab4:
    st.subheader("Vista de datos")

    if mostrar_tabla == "Sí":
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Se muestra una vista previa del dataset (primeras 10 filas):")
        st.dataframe(df.head(10), use_container_width=True)

    st.write("## Campeón del torneo")

    if st.button("Mostrar campeón"):

        final = df.tail(1).iloc[0]

        
        equipo1 = final["Team 1"].split(" › ")[0]
        equipo2 = final["Team 2"].split(" › ")[0]

        goles1 = int(final["FT"].split("-")[0])
        goles2 = int(final["FT"].split("-")[1])

        campeon = equipo1 if goles1 > goles2 else equipo2

        st.write(f"### Campeón: **{campeon}**")

        ruta = "barcelona_escudo.png"
       
        st.image(ruta, width=200)
         
        st.write("### Datos de la final:")
        st.dataframe(df.tail(1), use_container_width=True)





