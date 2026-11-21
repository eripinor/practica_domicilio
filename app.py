# Para ver la app, en la terminal escribir: streamlit run app.py

# ==========================================================
# PASO 1. LA PÁGINA
# ==========================================================

# Importar las librerías necesarias
import streamlit as st
import pandas as pd

# Configurar la página
st.set_page_config(
    page_title="La Consulta a domicilio", 
    page_icon="🛵", 
    layout="wide")

# page_title: nombre que aparece en la pestaña del navegador
# layout="wide": aprovecha todo el ancho de la pantalla

# Mostrar el título de la aplicación
st.title("La Consulta a domicilio")

# Explicar el contenido de la aplicación
st.write("Panel de análisis de los pedidos del bar La Consulta. Los datos incluyen pedidos, plataformas, barrios, tiempos de entrega, valoraciones y condiciones meteorológicas.")

# st.write(): muestra texto en la aplicación
st.write("El periodo analizado va del 1 de septiembre al 15 de noviembre de 2026.")


# ==========================================================
# PASO 2. LOS DATOS
# ==========================================================

# Crear una función para cargar los pedidos
@st.cache_data
def cargar_pedidos():
    return pd.read_csv("datos/pedidos_limpios.csv")

# @st.cache_data: guarda en caché los datos para evitar cargarlos innecesariamente
# pd.read_csv(): lee un archivo CSV y lo convierte en un DataFrame


# Crear una función para cargar los platos
@st.cache_data
def cargar_platos():
    return pd.read_csv("datos/platos.csv")


# Cargar las tablas
pedidos = cargar_pedidos()
platos = cargar_platos()


# ==========================================================
# PASO 3. LOS FILTROS
# ==========================================================

# Crear los filtros en la barra lateral
with st.sidebar:

    # Mostrar el título de los filtros
    st.header("Filtros")

    # Crear las opciones para la plataforma
    plataformas = ["Todas"] + sorted(pedidos["plataforma"].unique().tolist())

    # unique(): obtiene los valores únicos de una columna
    # tolist(): convierte los valores en una lista
    # sorted(): ordena los elementos alfabéticamente

    # Crear el desplegable de plataformas
    plataforma_seleccionada = st.selectbox("Plataforma", plataformas)
    # st.selectbox(): crea un desplegable para seleccionar una opción

    # Crear las opciones para los barrios
    barrios_disponibles = sorted(pedidos["barrio"].dropna().unique().tolist())
    # dropna(): elimina los valores nulos antes de obtener los barrios

    # Crear el desplegable de barrios
    barrio_seleccionado = st.selectbox("Barrio", ["Todos"] + barrios_disponibles)

    # Crear una barra para filtrar el importe del pedido
    importe_minimo = float(pedidos["total"].min())
    importe_maximo = float(pedidos["total"].max())
    # min(): obtiene el importe mínimo
    # max(): obtiene el importe máximo
    # float(): convierte el resultado en un número decimal

    importe_seleccionado = st.slider("Importe del pedido (€)", min_value=importe_minimo, max_value=importe_maximo, value=(importe_minimo, importe_maximo))
    # st.slider(): permite seleccionar un intervalo de valores
    # value=(...): establece el intervalo inicial, seleccionando todos los pedidos


# ==========================================================
# PASO 4. FILTRAR
# ==========================================================

# Crear una copia de los pedidos para aplicar los filtros
filtrados = pedidos.copy()
# copy(): crea una copia para trabajar sin modificar la tabla original

# Filtrar por plataforma
if plataforma_seleccionada != "Todas":
    filtrados = filtrados[filtrados["plataforma"] == plataforma_seleccionada]
# !=: significa distinto de

# Filtrar por barrio
if barrio_seleccionado != "Todos":
    filtrados = filtrados[filtrados["barrio"] == barrio_seleccionado]

# Filtrar por importe
filtrados = filtrados[(filtrados["total"] >= importe_seleccionado[0]) & (filtrados["total"] <= importe_seleccionado[1])]
# >=: mayor o igual que
# <=: menor o igual que
# &: combina dos condiciones que deben cumplirse simultáneamente


# ==========================================================
# PASO 5. SI NO QUEDA NADA
# ==========================================================

# Comprobar si hay pedidos después de aplicar los filtros
if filtrados.empty:

    # Mostrar un aviso si no hay resultados
    st.warning("No hay pedidos que coincidan con los filtros seleccionados.")
    # st.warning(): muestra un aviso

    # Detener la ejecución de la aplicación
    st.stop()
    # st.stop(): detiene la ejecución de Streamlit


# ==========================================================
# PASO 6. LAS MÉTRICAS
# ==========================================================

# Crear tres columnas para las métricas
col1, col2, col3 = st.columns(3)
# st.columns(): distribuye los elementos horizontalmente

# Mostrar el número de pedidos
col1.metric("Pedidos", len(filtrados))
# len(): cuenta el número de filas

# Mostrar el neto total del bar
col2.metric("Neto para el bar", f"{filtrados['neto'].sum():,.2f} €")
# sum(): suma los valores de la columna neto
# :.2f: muestra dos decimales

# Mostrar el tiempo medio de entrega
col3.metric("Tiempo medio", f"{filtrados['minutos'].mean():.2f} min")
# mean(): calcula la media de los valores
# :.2f: muestra dos decimales


# ==========================================================
# PASO 7. LAS PESTAÑAS
# ==========================================================

# Crear las pestañas de la aplicación
tab1, tab2, tab3 = st.tabs(["Pedidos", "Gráficos", "Platos"])
# st.tabs(): organiza el contenido en diferentes pestañas


# ----------------------------------------------------------
# PESTAÑA 1. PEDIDOS
# ----------------------------------------------------------

with tab1:

    # Mostrar el título
    st.subheader("Pedidos filtrados")

    # Mostrar la tabla filtrada
    st.dataframe(filtrados, use_container_width=True)
    # st.dataframe(): muestra una tabla interactiva
    # use_container_width=True: adapta la tabla al ancho disponible


# ----------------------------------------------------------
# PESTAÑA 2. GRÁFICOS
# ----------------------------------------------------------

with tab2:

    # Mostrar el título
    st.subheader("Análisis de los pedidos")

    # Crear el gráfico de pedidos por semana
    pedidos_semana = filtrados.groupby("semana").size()
    # groupby(): agrupa los pedidos por semana
    # size(): cuenta los pedidos de cada grupo

    st.write("### Pedidos por semana")
    st.line_chart(pedidos_semana)
    # st.line_chart(): crea un gráfico de líneas

    # Comparar el neto medio por plataforma
    neto_plataformas = filtrados.groupby("plataforma")["neto"].mean()
    # mean(): calcula el neto medio de cada plataforma

    st.write("### Neto medio por plataforma")
    st.bar_chart(neto_plataformas)
    # st.bar_chart(): crea un gráfico de barras

    # Calcular el tiempo medio por barrio
    tiempos_barrios = filtrados.groupby("barrio")["minutos"].mean()

    st.write("### Tiempo medio por barrio")
    st.bar_chart(tiempos_barrios)


# ----------------------------------------------------------
# PESTAÑA 3. PLATOS
# ----------------------------------------------------------

with tab3:

    # Mostrar el título
    st.subheader("Los platos más pedidos")

    # Ordenar los platos por unidades vendidas
    platos_ordenados = platos.sort_values("unidades_vendidas", ascending=False)
    # sort_values(): ordena los datos por una columna
    # ascending=False: ordena de mayor a menor

    # Seleccionar los 10 platos más pedidos
    top_10_platos = platos_ordenados.head(10)
    # head(10): selecciona las 10 primeras filas

    # Mostrar la tabla de los 10 platos más pedidos
    st.dataframe(top_10_platos, use_container_width=True)

    # Crear el gráfico de los 10 platos más pedidos
    grafico_platos = top_10_platos.set_index("plato")
    # set_index(): utiliza la columna plato como índice del DataFrame

    st.bar_chart(grafico_platos["unidades_vendidas"])


# ==========================================================
# PASO 8. UNA PREGUNTA PARA EL USUARIO
# ==========================================================

# Crear una pestaña para la pregunta del usuario
tab4 = st.tabs(["¿Cuánto tardará tu pedido?"])[0]

with tab4:

    # Mostrar el título
    st.subheader("¿Cuánto tardará tu pedido?")

    # Crear las opciones de barrios
    barrios_estimacion = sorted(pedidos["barrio"].dropna().unique().tolist())

    # Permitir elegir el barrio
    barrio_estimacion = st.selectbox("¿En qué barrio estás?", barrios_estimacion, key="barrio_estimacion")
    # key: identifica de forma única este widget dentro de la aplicación

    # Permitir indicar si llueve
    lluvia_estimacion = st.checkbox("Está lloviendo")
    # st.checkbox(): crea una casilla que devuelve True o False

    # Buscar los datos correspondientes al barrio y a la lluvia
    datos_estimacion = pedidos[(pedidos["barrio"] == barrio_estimacion) & (pedidos["llueve"] == lluvia_estimacion) & (pedidos["estado"] == "entregado")]
    # & combina las condiciones de búsqueda

    # Comprobar si existen datos con tiempos de entrega válidos
    tiempos_validos = datos_estimacion["minutos"].dropna()
    # dropna(): elimina los tiempos nulos antes de calcular la media

    if not tiempos_validos.empty:

        # Calcular el tiempo medio de entrega
        tiempo_estimado = tiempos_validos.mean()

        # Mostrar la estimación
        st.write(f"Según los datos históricos, en {barrio_estimacion} el tiempo medio de entrega es de {tiempo_estimado:.2f} minutos {'cuando llueve' if lluvia_estimacion else 'cuando no llueve'}.")
        # mean(): calcula el tiempo medio de entrega
        # La expresión condicional diferencia entre lluvia y ausencia de lluvia

    else:

        # Buscar los tiempos de entrega del barrio sin tener en cuenta la lluvia
        datos_barrio = pedidos[(pedidos["barrio"] == barrio_estimacion) & (pedidos["estado"] == "entregado")]["minutos"].dropna()

        # Comprobar si existen tiempos de entrega del barrio
        if not datos_barrio.empty:

            # Calcular el tiempo medio del barrio
            tiempo_estimado = datos_barrio.mean()

            # Mostrar un aviso
            st.info("No hay suficientes datos para esa combinación de barrio y lluvia. Se muestra el tiempo medio histórico del barrio sin tener en cuenta la lluvia.")

            # Mostrar la estimación alternativa
            st.write(f"El tiempo medio de entrega en {barrio_estimacion} es de {tiempo_estimado:.2f} minutos.")

        else:

            # Mostrar un aviso si tampoco existen datos del barrio
            st.warning("No hay datos suficientes para calcular una estimación.")
