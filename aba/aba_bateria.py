import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def exibir(dfs_por_arquivo, chart_type):
    st.subheader("🔋 Verificação de Bateria")

    encontrou_bateria = False

    for nome_arquivo, df in dfs_por_arquivo.items():
        campos_bateria = [c for c in df.columns if 'battery' in c.lower()]
        if not campos_bateria:
            continue

        encontrou_bateria = True
        st.markdown(f"### 📄 Arquivo: `{nome_arquivo}`")

        resumo = []

        for campo in campos_bateria:
            df[campo] = pd.to_numeric(df[campo], errors='coerce')

            # Filtrar tensões válidas (0 a 5V) para ignorar valores como -999
            df_validos = df[(df[campo] >= 0) & (df[campo] <= 5)]

            alerta = df_validos[(df_validos[campo] < 3.45) & (df_validos[campo] > 3.3)]
            critico = df_validos[df_validos[campo] <= 3.3]

            resumo.append({
                "Campo de Bateria": campo,
                "Leituras < 3.45V": len(alerta),
                "Leituras < 3.3V": len(critico)
            })

        df_resumo = pd.DataFrame(resumo)

        def destacar_celula(val, limite):
            if val > 0:
                if limite == 3.3:
                    return "background-color: red; color: white;"
                elif limite == 3.45:
                    return "background-color: orange; color: black;"
            return ""

        styled = df_resumo.style.map(lambda v: destacar_celula(v, 3.3), subset=["Leituras < 3.3V"])
        styled = styled.map(lambda v: destacar_celula(v, 3.45), subset=["Leituras < 3.45V"])

        st.dataframe(styled, use_container_width=True)

        with st.expander("📊 Gráficos e Métricas de Bateria"):
            busca = st.text_input("🔍 Buscar instrumento de bateria:", key=f"busca_{nome_arquivo}")

            campos_filtrados = [c for c in campos_bateria if busca.lower() in c.lower()]
            for campo in campos_filtrados:
                if 'timestamp' not in df.columns:
                    st.warning(f"⚠️ O campo `{campo}` do arquivo `{nome_arquivo}` será ignorado pois não possui coluna 'timestamp'.")
                    continue

                df_plot = df[['timestamp', campo]].dropna()
                df_plot = df_plot[(df_plot[campo] >= 0) & (df_plot[campo] <= 5)]  # Faixa válida
                df_plot['timestamp'] = pd.to_datetime(df_plot['timestamp'], errors='coerce')
                df_plot = df_plot.sort_values('timestamp')

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_plot['timestamp'], y=df_plot[campo],
                                         mode='lines',
                                         name=campo))

                fig.add_hline(y=3.45, line_dash="dot", line_color="orange", annotation_text="Alerta (3.45V)", annotation_position="top left")
                fig.add_hline(y=3.3, line_dash="dot", line_color="red", annotation_text="Crítico (3.3V)", annotation_position="bottom left")

                fig.update_layout(
                    title=f"{campo}",
                    xaxis_title="Timestamp",
                    yaxis_title="Tensão (V)",
                    height=300
                )

                st.plotly_chart(fig, use_container_width=True, key=f"{nome_arquivo}_{campo}_grafico")

    if not encontrou_bateria:
        st.success("✅ Nenhum campo de bateria encontrado nos arquivos carregados.")
