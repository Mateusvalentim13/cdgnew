# utils.py
import pandas as pd

def destacar_qtd_leituras(val):
    try:
        if float(val) == 0:
            return ""
        return "background-color: orange; color: black"
    except:
        return ""

def destacar_mudanca(val):
    try:
        if pd.isna(val):
            return ""
        elif float(val) == 0:
            return "background-color: yellow; color: black"
        return "background-color: #54e346; color: black"
    except:
        return ""

def destacar_falhas(val):
    try:
        if float(val) == -999:
            return "background-color: yellow; color: black"
    except:
        pass
    return ""

def detectar_erros_temporais(df_total):
    erros = []
    if 'timestamp' not in df_total.columns or 'arquivo_origem' not in df_total.columns:
        return pd.DataFrame()

    arquivos = df_total['arquivo_origem'].unique()

    for arquivo in arquivos:
        df_arquivo = df_total[df_total['arquivo_origem'] == arquivo].copy()
        df_arquivo = df_arquivo[['timestamp']].dropna().reset_index(drop=True)
        df_arquivo['timestamp'] = pd.to_datetime(df_arquivo['timestamp'], errors='coerce')

        for i in range(1, len(df_arquivo)):
            if df_arquivo['timestamp'].iloc[i] < df_arquivo['timestamp'].iloc[i - 1]:
                erros.append({
                    'Arquivo': arquivo,
                    'Linha': i,
                    'Timestamp anterior': df_arquivo['timestamp'].iloc[i - 1],
                    'Timestamp atual': df_arquivo['timestamp'].iloc[i]
                })

    return pd.DataFrame(erros)
