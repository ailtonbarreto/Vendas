import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Vendas Dashboard", page_icon=":bar_chart:", layout="wide")

#--------------------------------------------------------------------------------------------------
# Layout
col1, col2, col3, col4 = st.columns([4,4,1,1])
colleft, colleft1, colright, colright1 = st.columns(4)
col7, col8 = st.columns(2)
col9, col10 = st.columns([2,2])


#--------------------------------------------------------------------------------------------------
# Ler o Excel
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="Vendas.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=0,
    )
#--------------------------------------------------------------------------------------------------
# Coluna de horas no dataframe
    df["Dia Mês"] = pd.to_datetime(df["Data"]).dt.day
    return df

df = get_data_from_excel()
#--------------------------------------------------------------------------------------------------
#Definir mês

df['Ano'] = df["Data"].dt.year
df['Mês'] = df["Data"].dt.month
df['Dia'] = df["Data"].dt.dayofweek

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
    lojas = st.multiselect("Lojas",['Franca','Goioerê','Ribeirão Preto'],default=['Franca','Goioerê','Ribeirão Preto'])

df_selection = df.query("Ano == @ano == Ano & Mês ==@Mês & Cidade == @lojas") 

df_selection['Ordem_dia'] = df_selection['Dia'].map(classificar_dia)
df_selection = df_selection.sort_values(by='Ordem_dia',ascending = True).drop(columns=['Ordem_dia'])

#--------------------------------------------------------------------------------------------------
#Pagina principal
with col1:
    st.title(":bar_chart: Vendas Dashboard",anchor=False)
    st.markdown("##")

#--------------------------------------------------------------------------------------------------
# Indicadores
total_sales = int(df_selection["Total"].sum())
qtd_sales = int(df_selection["Nota Fiscal"].nunique())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = "⭐" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)


with colleft:
    st.markdown("""---""")
    st.subheader("QTD Vendas:",anchor=False)
    st.subheader(qtd_sales,anchor=False)
    st.markdown("""---""")
with colleft1:
    st.markdown("""---""")
    st.subheader("Total de Vendas:",anchor=False)
    st.subheader(f"  R${total_sales:,}",anchor=False)
    st.markdown("""---""")
with colright:
    st.markdown("""---""")
    st.subheader("Ticket Médio:",anchor=False)
    st.subheader(f"R$  {average_sale_by_transaction}",anchor=False)
    st.markdown("""---""")
with colright1:
    st.markdown("""---""")
    st.subheader("Média Toten:",anchor=False)
    st.subheader(f"{average_rating} {star_rating}",anchor=False)
    st.markdown("""---""")

#--------------------------------------------------------------------------------------------------
# Vendas por linha de produto
Vendas_Categoria = df_selection.groupby(by=["Categoria"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = px.bar(
    Vendas_Categoria,
    x="Total",
    y=Vendas_Categoria.index,
    orientation="h",
    title="<b>Vendas por Categoria</b>",
    color_discrete_sequence=["#0083B8"] * len(Vendas_Categoria),
    template="plotly_white",
)
fig_product_sales.update_layout(plot_bgcolor="rgba(0,0,0,0)",xaxis=(dict(showgrid=False)))

#--------------------------------------------------------------------------------------------------
# Vendas por dia no mês
vendas_diames = df_selection.groupby(by=["Dia Mês"])['Total'].sum().reset_index()

vendasmes = px.area(vendas_diames,x="Dia Mês",y="Total",title="Vendas do mês")

vendasmes.update_layout(xaxis=dict(tickmode="linear"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),)

#--------------------------------------------------------------------------------------------------
#Gráficos
grafico_rosca = px.pie(df_selection,names="Método de Pagamento",values="Total",color_discrete_sequence=["#0083B8"],title="Métodos de Pagamentos")


vendas_semana = df_selection.groupby(by=["Dia"])["Total"].sum().reset_index()
vendas_semana['Ordem_dia'] = vendas_semana['Dia'].map(classificar_dia)
vendas_semana = vendas_semana.sort_values(by='Ordem_dia',ascending = True).drop(columns=['Ordem_dia'])
grafico_semana = px.bar(vendas_semana,x='Dia',y='Total',title='Vendas da Semana',color_discrete_sequence=["#0083B8"])
grafico_semana.update_yaxes(showgrid=False)

vendas_produto = df_selection.groupby(by=["Produto"])[["Total"]].sum().sort_values(by="Total",ascending=False)

grafico_produto  = px.bar(vendas_produto,x="Total",y=vendas_produto.index,
    orientation="h",title="<b>Ranking De Vendedores</b>",color_discrete_sequence=["#0083B8"] * len(vendas_produto))

df_loja = df_selection.groupby(by='Cidade')['Total'].sum().reset_index()
vendas_lojas = px.pie(df_loja,names="Cidade",values="Total",color_discrete_sequence=["#0083B8"],title="Lojas")
vendas_lojas.update_yaxes(showgrid=False)

#--------------------------------------------------------------------------------------------------

with col7:
    st.plotly_chart(vendas_lojas,use_container_width=True)
with col8:
    st.plotly_chart(grafico_produto,use_container_width=True)
with col9:
    st.markdown("""---""")
    st.plotly_chart(vendasmes, use_container_width=True)
with col10:
    st.markdown("""---""")
    st.plotly_chart(grafico_semana,use_container_width=True)

st.markdown("""---""")

#--------------------------------------------------------------------------------------------------
# Esconder menu streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------------