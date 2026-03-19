import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from thefuzz import process

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Inmovision - Dashboard Corporativo", layout="wide")

# 2. CSS PARA DISEÑO UNIFICADO Y ESTILOS DE TARJETAS (NUEVOS ESTILOS PARA LA IMAGEN)
st.markdown("""
    <style>
    [data-testid="bundle-lib-sidebar-close-icon"], 
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    .stApp { background-color: #0e1117 !important; }
    .asesor-header { color: #ffffff; font-size: 26px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
    
    /* Contenedor principal de tarjetas */
    .card-container { display: flex; gap: 15px; margin-bottom: 25px; margin-top: 10px; }
    
    /* Estilo general de tarjeta (como las grises de tu código) */
    .card-total { background-color: #f1f3f6; border-radius: 10px; padding: 15px; flex: 1; color: #1a1c24; text-align: center; border-left: 5px solid #4CAF50; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); }
    .total-label { font-weight: 800; font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 5px; }
    .total-amount { font-size: 28px; font-weight: bold; color: #000; }
    
    /* --- NUEVOS ESTILOS PARA REPLICAR LA IMAGEN --- */
    .card-image-style {
        background-color: #ffffff; /* Fondo blanco */
        border-radius: 12px;
        padding: 20px;
        flex: 1;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        border: 1px solid #e1e4e8; /* Borde sutil */
    }
    .image-label {
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
        color: #7f8c8d; /* Color gris suave */
        margin-bottom: 10px;
    }
    .image-value-text {
        font-size: 32px;
        font-weight: 900;
        color: #1a1c24; /* Texto oscuro */
        text-transform: uppercase;
    }
    .image-value-number {
        font-size: 40px;
        font-weight: 900;
        color: #1a1c24; /* Número oscuro */
    }
    /* Decoradores de borde izquierdo */
    .border-green { border-left: 8px solid #2ecc71; }
    .border-blue { border-left: 8px solid #3498db; }
    /* Estilo para el título de la sección */
    .section-title-image {
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .section-icon { margin-right: 10px; }
    /* --- FIN NUEVOS ESTILOS --- */
    
    [data-testid="stSidebar"] { background-color: #1a1c24; }
    .logo-sidebar { display: block; margin: auto; width: 150px; margin-bottom: 20px; }
    .detalle-titulo { color: #ffffff; font-size: 20px; font-weight: bold; margin-top: 30px; margin-bottom: 10px; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. CONFIGURACIÓN DE RECURSOS
URL_VENTAS = "https://docs.google.com/spreadsheets/d/18WS22r1Fml5a9qW3fJOj40d0h7aldJVj/edit?usp=sharing"
URL_INSTALACIONES = "https://docs.google.com/spreadsheets/d/1QqH8lGktix5YLV7seIL9cXUxWCaANauM/edit?usp=sharing"
URL_GESTION = "https://docs.google.com/spreadsheets/d/1z_Y-dSghRs0nuFwOm6Eh_ZTPE-RKRVcj/edit?usp=sharing"
URL_LOGO = "https://lh4.googleusercontent.com/proxy/SeW7l23MFgElfFnJzA8WsomRRdBeiXYsMuQMdiB6_m4J0N0j7RGAB09PNGAO-uUPhKMPITGfAgagRh76fzbODUl3jU3utoz20hT2W99Q7BODxV-g" 

VENDEDORES_PERMITIDOS = [
    "ALEXANDRA REINO", "ANDREA MENDOZA", "CESAR VERA", "DIANA RIVERA", 
    "EDISON SACA", "FRANKLIN QUEZADA", "GLENDA RAMOS AYORA", "JENNIFER ATANCURI", 
    "JORGE GARCIA", "LAURA MORAN", "MANCHENO KARLA", "MARIA JOSE PEÑAFIEL", 
    "MELANY GUZHÑAY", "NANCY JARAMA", "PRISCILA RAMOS", "SILVIA YUNGA", 
    "STALIN ROJAS", "SUSANA PACURUCU", "VERONICA MALO", 
    "WILLIAM BRITO", "WILLIAN MOLINA"
]

# --- FUNCIÓN DE LIMPIEZA DE NOMBRES ---
def corregir_nombre(nombre_sucio, lista_maestra, umbral=90):
    if not nombre_sucio or pd.isna(nombre_sucio): return "DESCONOCIDO"
    nombre_sucio = str(nombre_sucio).strip().upper()
    # Reglas manuales críticas (Como Menddoza o Andrea)
    if "MENDD" in nombre_sucio or "ANDRE M" in nombre_sucio: return "ANDREA MENDOZA"
    if "PACURUCO" in nombre_sucio: return "SUSANA PACURUCU"
    if "AYORA GLENDA" in nombre_sucio: return "GLENDA RAMOS AYORA"
    
    match, score = process.extractOne(nombre_sucio, lista_maestra)
    return match if score >= umbral else nombre_sucio

@st.cache_data(ttl=600)
def cargar_datos(url, nombre_hoja):
    try:
        file_id = url.split('/')[-2]
        export_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'
        df = pd.read_excel(export_url, sheet_name=nombre_hoja)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except: return None

# --- SIDEBAR ---
st.sidebar.markdown(f'<img src="{URL_LOGO}" class="logo-sidebar">', unsafe_allow_html=True)
st.sidebar.title("Menú Principal")
seccion = st.sidebar.radio("Seleccione un Módulo:", ["📊 Control de Ventas", "🛠️ Reporte de Instalaciones", "📈 Gestión de Asesores"])
st.sidebar.markdown("---")

# ==========================================
# MÓDULO 1: CONTROL DE VENTAS (SIN CAMBIOS)
# ==========================================
if seccion == "📊 Control de Ventas":
    try:
        file_id_v = URL_VENTAS.split('/')[-2]
        xls = pd.ExcelFile(f'https://docs.google.com/spreadsheets/d/{file_id_v}/export?format=xlsx')
        hojas_reales = xls.sheet_names
        mapa_hojas = {str(h).lower(): h for h in hojas_reales}
        mes_sel_display = st.sidebar.selectbox("📅 Mes a consultar:", list(mapa_hojas.keys()))
        
        df_ventas = cargar_datos(URL_VENTAS, mapa_hojas[mes_sel_display])
        df_inst_conteo = cargar_datos(URL_INSTALACIONES, "Instalaciones")

        if df_ventas is not None:
            col_vendedor = df_ventas.columns[0]
            # Aplicamos corrección inteligente
            df_ventas[col_vendedor] = df_ventas[col_vendedor].apply(lambda x: corregir_nombre(x, VENDEDORES_PERMITIDOS))
            
            # Filtros Sidebar
            st.sidebar.markdown("### Filtros")
            ver_todo = st.sidebar.checkbox("Ver Resumen General del Mes")
            v_unicos = sorted(list(set([v for v in df_ventas[col_vendedor].unique() if v in VENDEDORES_PERMITIDOS])))
            vendedor_sel = st.sidebar.selectbox("👤 Seleccionar Asesor:", v_unicos)

            if ver_todo:
                st.markdown('<div class="asesor-header">📊 Resumen General de Ventas</div>', unsafe_allow_html=True)
                columnas_total = [c for c in df_ventas.columns if 'TOTAL' in str(c).upper() and c != col_vendedor]
                if columnas_total:
                    col_total_name = columnas_total[0]
                    resumen = df_ventas[df_ventas[col_vendedor].isin(VENDEDORES_PERMITIDOS)].copy()
                    resumen = resumen[[col_vendedor, col_total_name]]
                    resumen.columns = ['Vendedor', 'Monto Total']
                    resumen['Monto Total'] = pd.to_numeric(resumen['Monto Total'], errors='coerce').fillna(0)
                    resumen = resumen[resumen['Monto Total'] > 0].sort_values(by='Monto Total', ascending=False)
                    
                    st.markdown(f'<div style="background-color:#1a1c24; border:1px solid #4CAF50; border-radius:12px; padding:25px; text-align:center; margin-bottom:20px;"><div class="total-label" style="color:#4CAF50">Venta Total Consolidada</div><div style="font-size:45px; font-weight:bold; color:#4CAF50;">${resumen["Monto Total"].sum():,.2f}</div></div>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 1])
                    with c1: st.dataframe(resumen, use_container_width=True, hide_index=True)
                    with c2:
                        fig_pie = px.pie(resumen, values='Monto Total', names='Vendedor', hole=0.4, title="Participación")
                        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                        st.plotly_chart(fig_pie, use_container_width=True)

            elif vendedor_sel:
                st.markdown(f'<div class="asesor-header">👤 Asesor: {vendedor_sel}</div>', unsafe_allow_html=True)
                fila_v = df_ventas[df_ventas[col_vendedor] == vendedor_sel]
                
                cols_excluir = [col_vendedor] + [c for c in df_ventas.columns if 'TOTAL' in str(c).upper()]
                cols_datos = [c for c in df_ventas.columns if c not in cols_excluir]
                
                datos_fila = fila_v[cols_datos].T.reset_index().iloc[:, :2]
                datos_fila.columns = ['Fecha', 'Venta']
                datos_fila['Venta'] = pd.to_numeric(datos_fila['Venta'], errors='coerce').fillna(0)
                datos_fila['Fecha_DT'] = pd.to_datetime(datos_fila['Fecha'], errors='coerce')
                ventas_ok = datos_fila[datos_fila['Venta'] > 0].copy().sort_values('Fecha_DT')
                ventas_ok['Fecha_Limpia'] = ventas_ok['Fecha_DT'].dt.strftime('%d-%m-%Y')

                # Comprobación con Módulo Instalaciones
                cantidad_comprobada = 0
                if df_inst_conteo is not None:
                    df_inst_conteo['FECHA'] = pd.to_datetime(df_inst_conteo['FECHA'], errors='coerce')
                    df_inst_conteo['VENDEDOR'] = df_inst_conteo['VENDEDOR'].apply(lambda x: corregir_nombre(x, VENDEDORES_PERMITIDOS))
                    col_comp = 'PRECIO DEL PLAN CON IVA' if 'PRECIO DEL PLAN CON IVA' in df_inst_conteo.columns else df_inst_conteo.columns[-2]
                    
                    f_dt = datos_fila['Fecha_DT'].dropna()
                    if not f_dt.empty:
                        mask = (df_inst_conteo['VENDEDOR'] == vendedor_sel) & \
                               (df_inst_conteo['FECHA'] >= f_dt.min()) & \
                               (df_inst_conteo['FECHA'] <= f_dt.max()) & \
                               (pd.to_numeric(df_inst_conteo[col_comp], errors='coerce') > 0)
                        cantidad_comprobada = len(df_inst_conteo[mask])

                # Tarjetas
                st.markdown(f'''
                    <div class="card-container">
                        <div class="card-total"><div class="total-label">Monto Total Vendido</div><div class="total-amount">${ventas_ok["Venta"].sum():,.2f}</div></div>
                        <div class="card-total" style="border-left-color: #2196F3;"><div class="total-label">Ventas Comprobadas</div><div class="total-amount">{cantidad_comprobada}</div></div>
                    </div>''', unsafe_allow_html=True)
                
                if not ventas_ok.empty:
                    fig_vend = px.line(ventas_ok, x='Fecha_Limpia', y='Venta', title="Tendencia de Rendimiento", markers=True, color_discrete_sequence=['#00D4FF'])
                    fig_vend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_vend, use_container_width=True)
                    
                    st.markdown('<div class="detalle-titulo">📅 Detalle de Transacciones</div>', unsafe_allow_html=True)
                    st.dataframe(ventas_ok[['Fecha_Limpia', 'Venta']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error en ventas: {e}")

# ==========================================
# MÓDULO 2: REPORTE DE INSTALACIONES (MODIFICADO PARA REPLICAR LA IMAGEN)
# ==========================================
elif seccion == "🛠️ Reporte de Instalaciones":
    # El título se moverá más abajo para coincidir con el diseño
    # st.markdown('<div class="asesor-header">🛠️ Control de Instalaciones</div>', unsafe_allow_html=True)
    df_inst = cargar_datos(URL_INSTALACIONES, "Instalaciones")
    
    if df_inst is not None:
        if 'FECHA' in df_inst.columns:
            df_inst['FECHA'] = pd.to_datetime(df_inst['FECHA'], errors='coerce')
            df_inst = df_inst.dropna(subset=['FECHA'])
            
            # Limpieza de nombres en el módulo 2 también
            if 'VENDEDOR' in df_inst.columns:
                df_inst['VENDEDOR'] = df_inst['VENDEDOR'].apply(lambda x: corregir_nombre(x, VENDEDORES_PERMITIDOS))
            
            anios = sorted(df_inst['FECHA'].dt.year.unique(), reverse=True)
            # Valor predeterminado para el selector de año si está vacío
            anio_default = datetime.now().year if not anios else anios[0]
            anio_sel = st.sidebar.selectbox("📅 Seleccionar Año:", anios, index=0 if anios else None)
            vendedor_inst_sel = st.sidebar.selectbox("👤 Seleccionar Vendedor:", ["TODOS"] + sorted(VENDEDORES_PERMITIDOS))
            
            # Filtrado principal
            if anios:
                df_anio = df_inst[df_inst['FECHA'].dt.year == anio_sel].copy()
            else:
                df_anio = df_inst.copy() # O manejar como vacío si prefieres

            if vendedor_inst_sel != "TODOS":
                df_anio = df_anio[df_anio['VENDEDOR'] == vendedor_inst_sel]

            # Filtro adicional de estados en sidebar
            if 'ESTADO' in df_anio.columns:
                estados_unicos = sorted(df_anio['ESTADO'].dropna().astype(str).unique().tolist())
                estados_sel = st.sidebar.multiselect("📋 Filtrar por Estado:", estados_unicos, default=estados_unicos)
                df_f = df_anio[df_anio['ESTADO'].isin(estados_sel)].copy()
            else: df_f = df_anio.copy()

            # --- INICIO RÉPLICA DE LA IMAGEN ---
            
            # 1. CÁLCULO DE DATOS PARA TARJETAS SUPERIORES
            prod_estrella = "N/A"
            tipos_venta = 0
            if 'PRODUCTO' in df_f.columns and not df_f.empty:
                df_prod = df_f['PRODUCTO'].value_counts().reset_index()
                prod_estrella = df_prod.iloc[0]['PRODUCTO'] if not df_prod.empty else "N/A"
                tipos_venta = len(df_prod)

            # 2. RENDERIZADO DE TARJETAS SUPERIORES CON ESTILO DE LA IMAGEN
            st.markdown(f'''
                <div class="card-container">
                    <div class="card-image-style border-green">
                        <div class="image-label">Producto Estrella</div>
                        <div class="image-value-text">{prod_estrella}</div>
                    </div>
                    <div class="card-image-style border-blue">
                        <div class="image-label">Tipos de Venta</div>
                        <div class="image-value-number">{tipos_venta}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            # 3. TÍTULO DE LA SECCIÓN GRÁFICA (CON ICONO)
            st.markdown('<div class="section-title-image"><span class="section-icon">📊</span> Rendimiento por Estado</div>', unsafe_allow_html=True)

            # 4. GRÁFICO DE BARRAS HORIZONTALES "RENDIMIENTO POR ESTADO"
            if not df_f.empty and 'ESTADO' in df_f.columns:
                # Preparación de datos para el gráfico
                df_st = df_f['ESTADO'].value_counts().reset_index()
                df_st.columns = ['ESTADO', 'CANTIDAD']
                total_est = df_st['CANTIDAD'].sum()
                
                # Cálculo de porcentajes para las etiquetas
                df_st['PORCENTAJE'] = (df_st['CANTIDAD'] / total_est * 100).map('{:.1f}%'.format)
                df_st['ETIQUETA'] = df_st['CANTIDAD'].astype(str) + " (" + df_st['PORCENTAJE'] + ")"
                
                # Mapeo de colores específico para replicar la imagen
                color_map = {
                    "INSTALADO": "#82e0aa",    # Verde claro
                    "RECOORDINAR": "#f7d16d",   # Amarillo/Naranja suave
                    "POR INSTALAR": "#f2a679",  # Naranja
                    "NO INSTALADO": "#b997f0"   # Morado claro
                }
                # Definir color predeterminado para estados no mapeados
                df_st['COLOR'] = df_st['ESTADO'].map(color_map).fillna('#95a5a6') # Gris si no coincide

                # Creación del gráfico con Plotly Express
                fig_status = px.bar(
                    df_st, 
                    x='CANTIDAD', 
                    y='ESTADO', 
                    orientation='h', 
                    text='ETIQUETA', 
                    color='ESTADO',
                    color_discrete_map=color_map,
                    labels={'CANTIDAD': 'CANTIDAD', 'ESTADO': 'ESTADO'}
                )
                
                # Ajustes de diseño para que coincida con la imagen (fondo oscuro, sin leyendas, etc.)
                fig_status.update_layout(
                    height=500, # Ajustar altura según necesidad
                    paper_bgcolor='rgba(0,0,0,0)', # Fondo transparente para que use el del stApp
                    plot_bgcolor='rgba(0,0,0,0)',  # Fondo de la trama transparente
                    font_color="white",            # Color de fuente para etiquetas de ejes
                    showlegend=False,              # Ocultar la leyenda lateral
                    xaxis=dict(gridcolor='#333333'), # Color de línea de cuadrícula sutil
                    yaxis=dict(autorange="reversed") # Invertir eje Y para que INSTALADO quede arriba
                )
                # Ajustar posición del texto de la etiqueta (fuera de la barra)
                fig_status.update_traces(texttemplate='%{text}', textposition='outside', textfont_size=12)
                
                # Renderizar el gráfico en Streamlit
                st.plotly_chart(fig_status, use_container_width=True)

            # --- FIN RÉPLICA DE LA IMAGEN ---

            # Mantener el listado detallado expandible que tenías (es útil)
            with st.expander("Ver Listado Detallado de Registros"):
                st.markdown(f"### 📋 Listado Detallado - Año {anio_sel}")
                columnas_tabla = [c for c in ['CLIENTE', 'PRODUCTO', 'ESTADO', 'VENDEDOR'] if c in df_f.columns]
                st.dataframe(df_f[columnas_tabla], use_container_width=True, hide_index=True)

# ==========================================
# MÓDULO 3: GESTIÓN DE ASESORES (SIN CAMBIOS)
# ==========================================
elif seccion == "📈 Gestión de Asesores":
    st.markdown('<div class="asesor-header">📈 Reporte Diario de Gestión Unificado</div>', unsafe_allow_html=True)
    try:
        file_id_g = URL_GESTION.split('/')[-2]
        xls_g = pd.ExcelFile(f'https://docs.google.com/spreadsheets/d/{file_id_g}/export?format=xlsx')
        hojas_excluir = ['VARIABLES', 'VENTAS', 'TELEVENTAS', 'FACEBOOK', 'RETENCION']
        hojas_asesores = [h for h in xls_g.sheet_names if h.strip().upper() not in hojas_excluir]
        
        # Corrección: Asegurar que el selector no falle si hojas_asesores está vacío
        asesor_gestion = st.sidebar.selectbox("👤 Seleccionar Asesor para Gestión:", hojas_asesores if hojas_asesores else ["Sin Asesores"])
        
        if hojas_asesores:
            df_g = cargar_datos(URL_GESTION, asesor_gestion)
            
            if df_g is not None:
                col_est = 'ESTADO' if 'ESTADO' in df_g.columns else None
                if col_est:
                    df_g[col_est] = df_g[col_est].astype(str).str.strip().str.upper()
                    df_valido = df_g[df_g[col_est] != 'NAN'].copy()
                    firmados = len(df_valido[df_valido[col_est].str.contains("FIRMADO", na=False)])
                    gestion = len(df_valido[df_valido[col_est].str.contains("GESTI", na=False)])
                    
                    st.markdown(f"""
                        <div class="card-container">
                            <div class="card-total"><div class="total-label">Total Gestiones</div><div class="total-amount">{len(df_valido)}</div></div>
                            <div class="card-total" style="border-left-color: #4CAF50;"><div class="total-label">Firmados</div><div class="total-amount">{firmados}</div></div>
                            <div class="card-total" style="border-left-color: #FF9800;"><div class="total-label">En Gestión</div><div class="total-amount">{gestion}</div></div>
                        </div>""", unsafe_allow_html=True)
                    
                    if not df_valido.empty:
                        df_counts = df_valido[col_est].value_counts().reset_index()
                        df_counts.columns = ['Estado', 'Total']
                        fig_g = px.pie(df_counts, values='Total', names='Estado', hole=0.4, title=f"Estados de {asesor_gestion}")
                        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                        st.plotly_chart(fig_g, use_container_width=True)

                st.markdown("### 📄 Últimas Gestiones Registradas")
                cols_vista = [c for c in ['FECHA INICIO GESTIÓN', 'NOMBRE', 'ESTADO', 'COMENTARIOS'] if c in df_g.columns]
                st.dataframe(df_g[cols_vista].tail(20) if cols_vista else df_g.tail(20), use_container_width=True, hide_index=True)
        else:
            st.warning("No se encontraron hojas de asesores válidas en el archivo de gestión.")
    except Exception as e:
        st.error(f"Error en gestión: {e}")