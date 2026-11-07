import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard IBGE - Trabalho e Emprego", layout="wide")

st.title("Projeto Integrador - Números que Falam")
st.subheader("Indicador 6: Trabalho e População Empregada (PNAD Contínua - IBGE)")
st.write("Análise da taxa de desocupação (2012 x 2022), rendimento e informalidade por UF e sexo, pensando na Ministra do Trabalho, no presidente da CNI e na diretora do Sebrae.")


st.sidebar.header("Dados e Filtros")
arquivo = st.sidebar.file_uploader("Base IBGE (CSV ou XLSX)", type=["csv", "xlsx"])

if arquivo is None:
    df = pd.read_csv("dados_ibge_trabalho_2012_2022.csv")
elif arquivo.name.endswith(".csv"):
    df = pd.read_csv(arquivo)
else:
    df = pd.read_excel(arquivo)

regioes = sorted(df["Regiao"].unique())
regiao_sel = st.sidebar.multiselect("Região:", regioes, default=regioes)

ufs = sorted(df[df["Regiao"].isin(regiao_sel)]["UF"].unique())
uf_sel = st.sidebar.multiselect("UF:", ufs, default=ufs)

ano_sel = st.sidebar.selectbox("Ano:", [2022, 2012, "Todos (Comparativo)"])
sexo_sel = st.sidebar.radio("Sexo:", ["Ambos", "Homens", "Mulheres"])

df_view = df[df["Regiao"].isin(regiao_sel) & df["UF"].isin(uf_sel)]

if sexo_sel != "Ambos":
    df_view = df_view[df_view["Sexo"] == sexo_sel]

if ano_sel == "Todos (Comparativo)":
    df_ano = df_view
else:
    df_ano = df_view[df_view["Ano"] == ano_sel]

st.header("1. Métricas Estatísticas")

dados = df_ano["Taxa_Desocupacao"].dropna()

if len(dados) > 0:
    media = dados.mean()
    mediana = dados.median()
    moda = dados.mode()[0]
    q1 = dados.quantile(0.25)
    q3 = dados.quantile(0.75)
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    outliers = dados[(dados < lim_inf) | (dados > lim_sup)]
    desvio = dados.std()
    amplitude = dados.max() - dados.min()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Média", str(round(media, 2)) + "%")
    col2.metric("Mediana (Q2)", str(round(mediana, 2)) + "%")
    col3.metric("IQR (Q3 - Q1)", str(round(iqr, 2)) + "%")
    col4.metric("Desvio Padrão", str(round(desvio, 2)) + "%")
    col5.metric("Outliers", len(outliers))

    with st.expander("Ver quartis e regra dos outliers (1,5 x IQR)"):
        st.write("Q1:", round(q1, 2), "| Q2:", round(mediana, 2), "| Q3:", round(q3, 2))
        st.write("IQR:", round(iqr, 2))
        st.write("Limite inferior:", round(lim_inf, 2), "| Limite superior:", round(lim_sup, 2))
        st.write("Amplitude:", round(amplitude, 2), "| Mínimo:", round(dados.min(), 2), "| Máximo:", round(dados.max(), 2))
        st.write("Moda:", round(moda, 2))
else:
    st.warning("Nenhum dado para esses filtros.")

st.header("2. Gráficos")

tab1, tab2, tab3 = st.tabs(["2012 x 2022", "Boxplot", "Rendimento"])

with tab1:
    st.write("Taxa de desocupação média por UF")
    comparacao = df_view.groupby(["UF", "Ano"])["Taxa_Desocupacao"].mean().reset_index()
    st.bar_chart(comparacao, x="UF", y="Taxa_Desocupacao", color="Ano", stack=False)

with tab2:
    st.write("Boxplot da taxa de desocupação (a caixa é o IQR, a linha é a mediana e os pontos fora são os outliers)")
    fig, ax = plt.subplots()
    ax.boxplot(dados)
    ax.set_ylabel("Taxa de desocupação (%)")
    st.pyplot(fig)
    st.dataframe(df_ano[["UF", "Regiao", "Ano", "Sexo", "Taxa_Desocupacao", "Taxa_Informalidade", "Rendimento_Medio"]])

with tab3:
    st.write("Rendimento médio do trabalho: média x mediana")
    st.info("Média: R$ " + str(round(df_ano["Rendimento_Medio"].mean(), 2)) + " | Mediana: R$ " + str(round(df_ano["Rendimento_Medio"].median(), 2)))
    st.write("Se a média for maior que a mediana, é porque alguns rendimentos bem altos estão puxando a média pra cima.")

st.header("3. Perguntas de Negócio")

st.write("**1) Como a taxa de desocupação evoluiu de 2012 para 2022?**")
st.write(df.groupby("Ano")["Taxa_Desocupacao"].mean())
d22 = df[df["Ano"] == 2022]["Taxa_Desocupacao"]
st.write("Diferença entre o maior e o menor valor em 2022:", round(d22.max() - d22.min(), 2))

st.write("**2) Qual a diferença entre homens e mulheres?**")
st.write(df[df["Ano"] == 2022].groupby("Sexo")["Taxa_Desocupacao"].mean())

st.write("**3) Qual estado mais reduziu o desemprego?**")
tabela = df.pivot_table(index="UF", columns="Ano", values="Taxa_Desocupacao", aggfunc="mean")
tabela["Variacao"] = tabela[2022] - tabela[2012]
st.write(tabela.sort_values("Variacao").head(5))

st.header("4. Fontes")
st.write("PNAD Contínua (SIDRA/IBGE): https://sidra.ibge.gov.br/pesquisa/pnadca/")
st.write("Downloads do IBGE: https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html")

st.caption("Projeto Integrador - Etapa 3")