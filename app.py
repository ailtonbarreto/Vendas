import pandas as pd
import plotly.express as px
import streamlit as st
import datetime as dt

st.set_page_config(page_title="Vendas Dashboard", page_icon=":bar_chart:", layout="wide")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html = True)


#--------------------------------------------------------------------------------------------------
# Layout
col1, = st.columns(1)
col2, col3, col4 = st.columns([6,1,1])
colleft, colleft1, colright, colright1 = st.columns(4)
col7, col8 = st.columns(2)
col9, col10 = st.columns([2,2])

with col1:
    st.title('🏪 Performance das Lojas',anchor= False)
#--------------------------------------------------------------------------------------------------
# Ler o Excel

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSRxxA0fqxSJKjei6PHqaI48m3lVJzWENNnor-CUqkPbfbvGgBu-I1yOiUsPBnMZUBnMLNw97cg2X31/pub?output=csv"


#--------------------------------------------------------------------------------------------------

df = pd.read_csv(url)
df['Total'] = df["Total"].str.replace('.', '').str.replace(',', '.').astype(float)
df["Data"] = pd.to_datetime(df["Data"])
df['Ano'] = df["Data"].dt.year
df['Mês'] = df["Data"].dt.month
df['Dia'] = df["Data"].dt.dayofweek
df['Dia Mês'] = df['Data'].dt.day


#--------------------------------------------------------------------------------------------------

def determinar_mês(valor):
    meses = {
        1: "Jan",
        2: "Fev",
        3: "Mar",
        4: "Abr",
        5: "Mai",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Set",
        10: "Out",
        11: "Nov",
        12: "Dez"
    }
    return meses.get(valor)
df["Mês"] = df["Mês"].apply(determinar_mês)

#--------------------------------------------------------------------------------------------------

def determinar_dia(valor):
    dias = {
        0: "Seg",
        1: "Ter",
        2: "Qua",
        3: "Qui",
        4: "Sex",
        5: "Sab",
        6: "Dom"
    }
    return dias.get(valor)
df["Dia"] = df["Dia"].apply(determinar_dia)

#--------------------------------------------------------------------------------------------------
# classificar mês
classificar_dia = {'Seg':0,'Ter':1,'Qua':2,'Qui':3,'Sex':4,'Sab':5,'Dom':6}
classificar_meses = {'Jan':1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai':5, 'Jun': 6, 'Jul': 7, 'Ago': 8, 'Set':9, 'Out': 10, 'Nov': 11, 'Dez': 12}

df['Ordem_Mês'] = df['Mês'].map(classificar_meses)
df = df.sort_values(by='Ordem_Mês',ascending = True).drop(columns=['Ordem_Mês'])
#--------------------------------------------------------------------------------------------------
#Apoio seletor

meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
df = df.sort_values(by='Ano',ascending = False)
#--------------------------------------------------------------------------------------------------
# Barra lateral
with col4:
    Mês = st.selectbox('Mês',meses)
    
with col3:
    ano = st.selectbox("Ano",df["Ano"].unique())
    
with col2:
    lojas = st.multiselect("Lojas",df['Cidade'].unique(),default= df['Cidade'].unique())

df_selection = df.query("Ano == @ano == Ano & Mês ==@Mês & Cidade == @lojas") 

df_selection['Ordem_dia'] = df_selection['Dia'].map(classificar_dia)
df_selection = df_selection.sort_values(by='Ordem_dia',ascending = True).drop(columns=['Ordem_dia'])

#--------------------------------------------------------------------------------------------------
# Indicadores
total_sales = int(df_selection["Total"].sum())
qtd_sales = int(df_selection["Nota Fiscal"].nunique())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = "⭐" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)


with colleft:
    st.subheader("QTD Vendas:",anchor=False)
    st.subheader(qtd_sales,anchor=False)
with colleft1:
    st.subheader("Total de Vendas:",anchor=False)
    st.subheader(f"R$ {total_sales:,}",anchor=False)
with colright:
    st.subheader("Ticket Médio:",anchor=False)
    st.subheader(f"R$ {average_sale_by_transaction}",anchor=False)
with colright1:
    st.subheader("Média Toten:",anchor=False)
    st.subheader(f"{average_rating} {star_rating}",anchor=False)

#--------------------------------------------------------------------------------------------------
# Vendas por dia no mês
vendas_diames = df_selection.groupby(by=["Dia Mês"])['Total'].sum().reset_index()

vendasmes = px.area(vendas_diames,x="Dia Mês",y="Total",title=f'Vendas de {Mês} de {ano}')

vendasmes.update_layout(xaxis=dict(tickmode="linear"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),)

#--------------------------------------------------------------------------------------------------
#Gráficos
vendas_semana = df_selection.groupby(by=["Dia"])["Total"].sum().reset_index()
vendas_semana['Ordem_dia'] = vendas_semana['Dia'].map(classificar_dia)

vendas_semana = vendas_semana.sort_values(by='Ordem_dia',ascending = True).drop(columns=['Ordem_dia'])

grafico_semana = px.bar(vendas_semana,x='Dia',y='Total',text=vendas_semana["Total"].apply(lambda x: f'R$ {x:,.2f}'),
            title='Vendas da Semana',color_discrete_sequence=["#0083B8"])

grafico_semana.update_yaxes(showgrid=False)
grafico_semana.update_traces(textfont=dict(size=15,color='#ffffff'),textposition="auto")
#--------------------------------------------------------------------------------------------------

vendas_produto = df_selection.groupby(by=["Vendedor"])[["Total"]].sum().sort_values(by="Total",ascending=True)
vendas_produto = vendas_produto.sort_values("Total",ascending=False)
vendas_produto["Total"] = vendas_produto["Total"].apply(lambda x: f'R$ {x:,.2f}')

#--------------------------------------------------------------------------------------------------

df_loja = df_selection.groupby(by='Cidade')['Total'].sum().reset_index()
vendas_lojas = px.pie(df_loja,names="Cidade",values="Total",
        color_discrete_sequence=["#0083B8"],title="Lojas")
vendas_lojas.layout.xaxis.fixedrange = True
vendas_lojas.layout.yaxis.fixedrange = True
vendas_lojas.update_layout(showlegend=True)
vendas_lojas.update_yaxes(showgrid=False)
vendas_lojas.update_traces(textfont=dict(size=20,color='#ffffff'),textposition="auto")

#--------------------------------------------------------------------------------------------------

with col7:
    st.plotly_chart(vendas_lojas,use_container_width=True)
with col8:
    st.subheader("Ranking de Vendedores",anchor=False)
    st.dataframe(vendas_produto,use_container_width=True,column_config={"Produto":st.column_config.TextColumn(width='large')})
with col9:
    st.plotly_chart(vendasmes, use_container_width=True)
with col10:
    st.plotly_chart(grafico_semana,use_container_width=True)


#--------------------------------------------------------------------------------------------------
# Esconder menu streamlit

borderselect = """
    <style>
    [data-testid="column"]
    {
    padding: 15px;
    background-color: #242B31;
    border-radius: 12px;
    text-align: center;
    }
    </style>
"""
st.markdown(borderselect,unsafe_allow_html=True)


detalhes = """
    <style>
    [class="modebar-container"]
    {
    visibility: hidden;
    }
    </style>
"""

st.markdown(detalhes,unsafe_allow_html=True)

desativartelacheia = """
    <style>
    [data-testid="StyledFullScreenButton"]
    {
    visibility: hidden;
    }
    </style>
"""
st.markdown(desativartelacheia,unsafe_allow_html=True)


