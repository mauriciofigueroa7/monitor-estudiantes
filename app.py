import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Monitor de Seguimiento", layout="wide", page_icon="📊")

# --- FUNCIÓN: GENERAR HTML DEL CORREO (VISUAL) ---
def generar_html_correo(nombre, minutos, estado, color_estado, promedio_curso, min_curso, max_curso):
    # Definir color del texto según fondo (simple)
    text_color = "#5a5a5a"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); overflow: hidden; }}
        .header {{ background-color: #262730; color: white; padding: 20px; text-align: center; }}
        .stat-box {{ display: flex; justify-content: space-between; padding: 20px; background-color: {color_estado}33; border-left: 5px solid {color_estado}; margin: 20px; border-radius: 5px; }}
        .number {{ font-size: 32px; font-weight: bold; color: #262730; }}
        .label {{ font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .kpi-row {{ display: flex; justify-content: space-between; padding: 0 20px 20px 20px; }}
        .kpi {{ text-align: center; width: 30%; background: #f9f9f9; padding: 10px; border-radius: 8px; }}
        .footer {{ background-color: #f4f6f9; padding: 15px; text-align: center; font-size: 12px; color: #888; }}
        .status-badge {{ background-color: {color_estado}; color: #333; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
    </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📊 Informe Semanal de Seguimiento</h2>
                <p>Hola, {nombre}</p>
            </div>
            
            <div style="padding: 20px;">
                <p style="color: #666;">Aquí tienes el resumen de tu actividad en la plataforma esta semana.</p>
            </div>

            <!-- TARJETA PRINCIPAL DEL ESTUDIANTE -->
            <div class="stat-box">
                <div>
                    <div class="label">Tu Dedicación</div>
                    <div class="number">{minutos} min</div>
                </div>
                <div style="text-align: right;">
                    <div class="label">Estado</div>
                    <span class="status-badge">{estado}</span>
                </div>
            </div>

            <h3 style="padding-left: 20px; color: #444;">Comparativa del Grupo</h3>
            
            <!-- RESUMEN GRUPAL (KPIS) -->
            <div class="kpi-row">
                <div class="kpi">
                    <div style="font-size: 20px; font-weight: bold; color: #e74c3c;">{min_curso}</div>
                    <div style="font-size: 10px;">Mínimo</div>
                </div>
                <div class="kpi">
                    <div style="font-size: 20px; font-weight: bold; color: #3498db;">{promedio_curso:.0f}</div>
                    <div style="font-size: 10px;">Promedio</div>
                </div>
                <div class="kpi">
                    <div style="font-size: 20px; font-weight: bold; color: #2ecc71;">{max_curso}</div>
                    <div style="font-size: 10px;">Máximo</div>
                </div>
            </div>

            <div class="footer">
                <p>Este es un mensaje automático generado por el Sistema de Seguimiento.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- FUNCIÓN: CLASIFICACIÓN DE DATOS ---
def clasificar(minutos):
    # Ajusta estos umbrales según tu criterio
    if minutos < 60:
        return "MUY BAJA", "#FFCDD2", "🔴" # Rojo
    elif minutos < 200:
        return "BAJA", "#FFF9C4", "🟡" # Amarillo
    else:
        return "NORMAL", "#C8E6C9", "🟢" # Verde

# --- INTERFAZ PRINCIPAL ---
def main():
    st.title("📊 Dashboard de Seguimiento Académico")
    st.markdown("Sube tu archivo Excel para analizar y enviar reportes.")

    # 1. Carga de Archivo
    uploaded_file = st.file_uploader("Subir Excel (.xlsx)", type=['xlsx'])

    if uploaded_file:
        # Leer datos
        try:
            df = pd.read_excel(uploaded_file)
            
            # Verificar columnas necesarias
            req_cols = ['Nombre', 'Email', 'Minutos'] # Asegúrate que tu Excel tenga estas cabeceras
            if not all(col in df.columns for col in req_cols):
                st.error(f"El Excel debe tener las columnas: {req_cols}")
                return

            # Procesar datos
            df['Estado'], df['Color_Hex'], df['Icono'] = zip(*df['Minutos'].apply(clasificar))
            
            # Métricas Globales
            promedio = df['Minutos'].mean()
            minimo = df['Minutos'].min()
            maximo = df['Minutos'].max()
            total_min = df['Minutos'].sum()

            # --- VISUALIZACIÓN TIPO DASHBOARD (Tu Captura) ---
            
            # KPIs Superiores
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Mínimo", f"{minimo} min", delta_color="inverse")
            kpi2.metric("Máximo", f"{maximo} min")
            kpi3.metric("Promedio", f"{promedio:.1f} min")
            kpi4.metric("Total Grupo", f"{total_min} min")

            st.markdown("---")

            # Tabla Detallada con Estilo
            col_tabla, col_grafico = st.columns([2, 1])
            
            with col_tabla:
 		st.subheader("Listado de Estudiantes")
                
                # Función para asignar colores basada en el TEXTO de la celda
                def colorear_celdas(val):
                    color = 'white' # Por defecto
                    font_color = 'black'
                    
                    if val == 'MUY BAJA':
                        color = '#FFCDD2' # Rojo claro
                    elif val == 'BAJA':
                        color = '#FFF9C4' # Amarillo claro
                    elif val == 'NORMAL':
                        color = '#C8E6C9' # Verde claro
                        
                    return f'background-color: {color}; color: {font_color}'

                # Aplicamos el estilo usando la función correcta
                st.dataframe(
                    df[['Nombre', 'Minutos', 'Estado', 'Icono']].style.applymap(
                        colorear_celdas, subset=['Estado']
                    ),
                    use_container_width=True
                )

            with col_grafico:
                st.subheader("Distribución")
                fig = px.pie(df, names='Estado', hole=0.4, color='Estado',
                             color_discrete_map={'MUY BAJA':'#FFCDD2', 'BAJA':'#FFF9C4', 'NORMAL':'#C8E6C9'})
                st.plotly_chart(fig, use_container_width=True)

            # --- SECCIÓN DE ENVÍO DE CORREOS ---
            st.markdown("---")
            st.header("📧 Envío de Reportes")
            
            with st.expander("Ver Vista Previa del Correo (HTML)"):
                ejemplo = df.iloc[0]
                html_preview = generar_html_correo(ejemplo['Nombre'], ejemplo['Minutos'], 
                                                 ejemplo['Estado'], ejemplo['Color_Hex'], 
                                                 promedio, minimo, maximo)
                st.components.v1.html(html_preview, height=500, scrolling=True)

            # Formulario para credenciales (O usar st.secrets en producción)
            st.warning("Nota: Para enviar correos necesitas un 'App Password' de Gmail o tu servidor SMTP.")
            
            col_email1, col_email2 = st.columns(2)
            remitente = col_email1.text_input("Tu Correo (Gmail)", "profesor@ejemplo.com")
            password = col_email2.text_input("Contraseña de Aplicación", type="password")
            
            if st.button("🚀 Enviar Correos a Todos"):
                if not password:
                    st.error("Por favor ingresa la contraseña.")
                else:
                    bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Configurar Servidor SMTP (Ejemplo Gmail)
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(remitente, password)
                        
                        for i, row in df.iterrows():
                            # Crear Mensaje
                            msg = MIMEMultipart()
                            msg['From'] = remitente
                            msg['To'] = row['Email']
                            msg['Subject'] = f"📈 Reporte Semanal: {row['Nombre']}"
                            
                            # Generar HTML personalizado
                            html_content = generar_html_correo(
                                row['Nombre'], row['Minutos'], row['Estado'], row['Color_Hex'],
                                promedio, minimo, maximo
                            )
                            msg.attach(MIMEText(html_content, 'html'))
                            
                            # Enviar
                            server.send_message(msg)
                            
                            # Actualizar barra
                            progreso = (i + 1) / len(df)
                            bar.progress(progreso)
                            status_text.text(f"Enviado a: {row['Nombre']}")
                        
                        server.quit()
                        st.success("¡Todos los correos han sido enviados con éxito!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Ocurrió un error al enviar: {e}")

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

if __name__ == "__main__":
    main()