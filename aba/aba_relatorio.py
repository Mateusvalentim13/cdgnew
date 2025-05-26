import streamlit as st
import pandas as pd
from fpdf import FPDF
import numpy as np
import base64
import tempfile
from datetime import datetime
from utils.encoded_image import encoded_image

def exibir_relatorio_falhas(dfs_por_arquivo):
    st.subheader("Relatório de Falhas por Arquivo")

    if not dfs_por_arquivo:
        st.info("Nenhum arquivo carregado.")
        return

    # Decodificar a imagem base64 e salvar temporariamente
    logo_data = base64.b64decode(encoded_image)
    temp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_logo.write(logo_data)
    temp_logo.close()

    # Opções de seleção
    st.markdown("### Selecione os tipos de falhas a incluir no relatório:")
    incluir_comunicacao = st.checkbox("Falhas de comunicação)", value=True)
    incluir_patamar = st.checkbox("Mudança de patamar", value=True)
    incluir_disponibilidade = st.checkbox("Disponibilidade", value=True)
    incluir_bateria = st.checkbox("Status da bateria", value=True)
    incluir_congelamento = st.checkbox("Dados congelados", value=True)
    incluir_continuidade = st.checkbox("Continuidade temporal", value=True)
    incluir_sinal = st.checkbox("Qualidade do sinal (RSSIB/RSSIL > 75)", value=True)

    if st.button("Gerar Relatório em PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        limiar_variacao = 10  # Limiar padrão para mudança de patamar

        for nome_arquivo, df in dfs_por_arquivo.items():
            pdf.add_page()

            # Adiciona a logo no topo
            pdf.image(temp_logo.name, x=10, y=10, w=50)
            pdf.ln(25)  # espaço abaixo da logo

            pdf.set_fill_color(30, 144, 255)
            pdf.set_text_color(255)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "GeoWise - Relatório de Falhas", ln=True, fill=True)

            pdf.set_text_color(0)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Arquivo: {nome_arquivo}", ln=True)

            # Conversão timestamp
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
                df = df.sort_values('timestamp')

            # Falhas de comunicação
            if incluir_comunicacao:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Falhas de Comunicação:", ln=True)
                pdf.set_font("Arial", '', 11)
                
                col_relevantes = [col for col in df.columns if col.lower().endswith(('_digit', '_hz', '_mm', '_kpa', '_temp'))]
                falhas_detectadas = False
                
                for col in col_relevantes:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    falhas = df[df[col].isin([-999.0, -998.0])]
                    if not falhas.empty:
                        falhas_detectadas = True
                        for _, row in falhas.iterrows():
                            ts = row['timestamp']
                            val = row[col]
                            pdf.multi_cell(0, 10, f"{col} - {ts} - Valor: {val}")
                
                if not falhas_detectadas:
                    pdf.multi_cell(0, 10, "Nenhuma falha de comunicação encontrada.")


            # Mudança de patamar
            if incluir_patamar:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Mudança de Patamar:", ln=True)
                pdf.set_font("Arial", '', 11)
                
                col_relevantes = [col for col in df.columns if col.lower().endswith(('_digit', '_hz', '_mm', '_kpa', '_temp'))]
                mudancas_detectadas = False

                for col in col_relevantes:
                    serie = pd.to_numeric(df[col], errors='coerce').replace([-999, -998], np.nan).dropna()
                    diff = serie.diff().abs()
                    mudancas = serie[diff > limiar_variacao]
                    
                    if not mudancas.empty:
                        mudancas_detectadas = True
                        for idx in mudancas.index:
                            ts = df.loc[idx, 'timestamp']
                            val = df.loc[idx, col]
                            pdf.multi_cell(0, 10, f"{col} - {ts} - Mudança: {val}")
                
                if not mudancas_detectadas:
                    pdf.multi_cell(0, 10, "Nenhuma mudança significativa de patamar.")


            # Disponibilidade
            if incluir_disponibilidade:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Disponibilidade:", ln=True)
                pdf.set_font("Arial", '', 11)
                col_digit_cols = [col for col in df.columns if col.lower().endswith(('_digit', '_hz', '_mm', '_kpa'))]
                if col_digit_cols:
                    total = len(df) * len(col_digit_cols)
                    nao_nulos = df[col_digit_cols].replace([-999, -998], np.nan).notna().sum().sum()
                    disponibilidade = 100 * nao_nulos / total if total > 0 else 0
                    pdf.multi_cell(0, 10, f"Disponibilidade geral: {disponibilidade:.2f}%")
                else:
                    pdf.multi_cell(0, 10, "Nenhuma coluna relevante para cálculo de disponibilidade.")

            # Status da bateria
            if incluir_bateria:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Status da Bateria:", ln=True)
                pdf.set_font("Arial", '', 11)
                campos_bateria = [c for c in df.columns if 'battery' in c.lower()]
                algum_alerta = False
                if campos_bateria:
                    for campo in campos_bateria:
                        df[campo] = pd.to_numeric(df[campo], errors='coerce')
                        validos = df[(df[campo] >= 0) & (df[campo] <= 5)]
                        alerta = validos[(validos[campo] < 3.45) & (validos[campo] > 3.3)]
                        critico = validos[validos[campo] <= 3.3]
                        if len(alerta) + len(critico) > 0:
                            algum_alerta = True
                            pdf.multi_cell(0, 10, f"{campo}: Alertas <3.45V: {len(alerta)}, Críticos <=3.3V: {len(critico)}")
                    if not algum_alerta:
                        pdf.multi_cell(0, 10, "Nenhuma falha crítica ou alerta de bateria encontrada.")
                else:
                    pdf.multi_cell(0, 10, "Nenhuma coluna de bateria encontrada.")

            # Dados congelados
            if incluir_congelamento:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Dados Congelados:", ln=True)
                pdf.set_font("Arial", '', 11)
                colunas_validas = [col for col in df.columns if col not in ['timestamp'] and df[col].dtype in ['float64', 'int64']]
                congelamentos = []
                for col in colunas_validas:
                    serie = pd.to_numeric(df[col], errors='coerce')
                    blocos = (serie != serie.shift()).cumsum()
                    grupos = df.groupby([blocos, serie])
                    for (_, valor), grupo in grupos:
                        if len(grupo) >= 3 and pd.notna(valor):
                            congelamentos.append((col, grupo['timestamp'].iloc[0], grupo['timestamp'].iloc[-1]))
                if congelamentos:
                    for col, inicio, fim in congelamentos:
                        pdf.multi_cell(0, 10, f"{col}: de {inicio} até {fim}")
                else:
                    pdf.multi_cell(0, 10, "Nenhum dado congelado encontrado.")

            # Continuidade temporal
            # Qualidade do sinal RSSIB/RSSIL > 75
            if incluir_sinal:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Falhas de Sinal (RSSIB/RSSIL):", ln=True)
                pdf.set_font("Arial", '', 11)
                col_sinal = [col for col in df.columns if isinstance(col, str) and (
                    col.strip().upper().strip("'\"").endswith("RSSIB") or
                    col.strip().upper().strip("'\"").endswith("RSSIL")
                )]
                if col_sinal:
                    falhas_sinal = []
                    for col in col_sinal:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        falhas = df[df[col] > 75]
                        if not falhas.empty:
                            for _, row in falhas.iterrows():
                                ts = row['timestamp']
                                val = row[col]
                                falhas_sinal.append(f"{col} - {ts} - Valor: {val}")
                    if falhas_sinal:
                        for linha in falhas_sinal:
                            pdf.multi_cell(0, 10, linha)
                    else:
                        pdf.multi_cell(0, 10, "Nenhuma falha de sinal detectada.")
                else:
                    pdf.multi_cell(0, 10, "Nenhuma coluna de sinal encontrada.")

            if incluir_continuidade:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Quebras de Continuidade Temporal:", ln=True)
                pdf.set_font("Arial", '', 11)
                if 'timestamp' in df.columns:
                    df['timestamp_anterior'] = df['timestamp'].shift(1)
                    quebras = df[df['timestamp'] < df['timestamp_anterior']]
                    if not quebras.empty:
                        for _, row in quebras.iterrows():
                            pdf.multi_cell(0, 10, f"Linha {row.name}: {row['timestamp_anterior']} -> {row['timestamp']}")
                    else:
                        pdf.multi_cell(0, 10, "Nenhuma quebra na ordem cronológica.")
                else:
                    pdf.multi_cell(0, 10, "Coluna 'timestamp' não encontrada.")

            # Rodapé
            pdf.set_y(-15)
            pdf.set_font("Arial", 'I', 8)
            pdf.set_text_color(128)
            pdf.cell(0, 10, f"GeoWise Health Check - Página {pdf.page_no()}", align='C')

        # Gerar nome do arquivo com data
        data_atual = datetime.now().strftime("%d_%m_%Y")
        nome_arquivo = f"relatorio_{data_atual}.pdf"

        # Gerar PDF em memória
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.success("Relatório gerado com sucesso!")
        st.download_button(
            label="Baixar Relatório em PDF",
            data=pdf_bytes,
            file_name=nome_arquivo,
            mime="application/pdf"
        )
