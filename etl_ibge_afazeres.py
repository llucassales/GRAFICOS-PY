import pandas as pd
import numpy as np

def carregar_e_tratar_dados(caminho_csv):
    """
    Carrega e higieniza os dados da PNAD Contínua do IBGE referentes aos Afazeres Domésticos.
    """
    df = pd.read_csv(caminho_csv)
    
    # Tratamento de nulos e tipos de dados
    df['Horas_Afazeres_Domesticos'] = pd.to_numeric(df['Horas_Afazeres_Domesticos'], errors='coerce')
    df['Horas_Cuidado_Pessoas'] = pd.to_numeric(df['Horas_Cuidado_Pessoas'], errors='coerce')
    df['Total_Horas_Trabalho_Nao_Remunerado'] = pd.to_numeric(df['Total_Horas_Trabalho_Nao_Remunerado'], errors='coerce')
    
    df.dropna(subset=['Horas_Afazeres_Domesticos', 'Total_Horas_Trabalho_Nao_Remunerado'], inplace=True)
    return df

def calcular_estatisticas_completas(series, nome_metrica="Horas"):
    """
    Calcula as estatísticas descritivas completas exigidas pela rubrica da atividade.
    """
    q1 = float(np.percentile(series, 25))
    q2 = float(np.percentile(series, 50))  # Mediana
    q3 = float(np.percentile(series, 75))
    iqr = q3 - q1
    
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    
    outliers = series[(series < limite_inferior) | (series > limite_superior)].tolist()
    
    # Moda
    mode_val = series.mode()
    moda = float(mode_val.iloc[0]) if not mode_val.empty else q2

    return {
        'Métrica': nome_metrica,
        'Média': round(float(series.mean()), 2),
        'Mediana': round(q2, 2),
        'Moda': round(moda, 2),
        'Q1 (25%)': round(q1, 2),
        'Q2 (50%)': round(q2, 2),
        'Q3 (75%)': round(q3, 2),
        'IQR': round(iqr, 2),
        'Limite Inferior Outlier': round(limite_inferior, 2),
        'Limite Superior Outlier': round(limite_superior, 2),
        'Qtd Outliers': len(outliers),
        'Outliers': outliers,
        'Amplitude': round(float(series.max() - series.min()), 2),
        'Desvio Padrão': round(float(series.std()), 2),
        'Mínimo': round(float(series.min()), 2),
        'Máximo': round(float(series.max()), 2)
    }

if __name__ == '__main__':
    caminho = '/workspace/scratch/dados_ibge_afazeres_domesticos_2022.csv'
    df = carregar_e_tratar_dados(caminho)
    
    print("=== ESTATÍSTICAS GERAIS - AFAZERES DOMÉSTICOS ===")
    est_geral = calcular_estatisticas_completas(df['Horas_Afazeres_Domesticos'], "Horas Afazeres Domésticos")
    for k, v in est_geral.items():
        print(f"{k}: {v}")
        
    print("\n=== COMPARATIVO POR GÊNERO (HORAS SEMANAIS) ===")
    df_fem = df[df['Sexo'] == 'Feminino']['Horas_Afazeres_Domesticos']
    df_masc = df[df['Sexo'] == 'Masculino']['Horas_Afazeres_Domesticos']
    
    est_fem = calcular_estatisticas_completas(df_fem, "Mulheres")
    est_masc = calcular_estatisticas_completas(df_masc, "Homens")
    
    print("\n-- Mulheres --")
    for k, v in est_fem.items():
        print(f"  {k}: {v}")
        
    print("\n-- Homens --")
    for k, v in est_masc.items():
        print(f"  {k}: {v}")

    print("\n=== DESIGUALDADE RACIAL E GÊNERO (MEDIA DE HORAS AFAZERES + CUIDADO) ===")
    pivot_raca = df.groupby(['Sexo', 'Raca_Cor'])[['Horas_Afazeres_Domesticos', 'Horas_Cuidado_Pessoas', 'Total_Horas_Trabalho_Nao_Remunerado']].mean().round(2)
    print(pivot_raca)
