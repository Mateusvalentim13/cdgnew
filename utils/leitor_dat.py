import pandas as pd
import re
from io import StringIO

def ler_arquivo_dat_bruto(caminho):
    """
    Lê arquivos .dat brutos com possível presença de aspas duplas inconsistentes
    e cabeçalhos não padronizados, de forma robusta e reutilizável.

    Parâmetros:
    - caminho: caminho completo do arquivo .dat a ser lido

    Retorna:
    - DataFrame pandas com os dados carregados
    """
    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        linhas = f.readlines()

    # Corrige aspas duplas malformadas (ex: ""campo"") para "campo"
    linhas_corrigidas = [linha.replace('""', '"').strip() for linha in linhas]

    # Detectar primeira linha de dados com timestamp
    linha_inicio = next(
        (i for i, linha in enumerate(linhas_corrigidas)
         if re.match(r'^"?\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"?', linha)),
        None
    )
    if linha_inicio is None:
        raise ValueError("Não foi possível detectar linha de dados válida no arquivo .dat.")

    # Tentar detectar cabeçalho (linha anterior aos dados)
    linha_cabecalho = linha_inicio - 1 if linha_inicio > 0 else None
    if linha_cabecalho is not None:
        header_line = linhas_corrigidas[linha_cabecalho]
        if re.search(r'[a-zA-Z]', header_line):
            header = 0
            conteudo = '\n'.join(linhas_corrigidas[linha_cabecalho:])
        else:
            header = None
            conteudo = '\n'.join(linhas_corrigidas[linha_inicio:])
    else:
        header = None
        conteudo = '\n'.join(linhas_corrigidas[linha_inicio:])

    return pd.read_csv(StringIO(conteudo), header=header, na_values=["-999", '""'])
