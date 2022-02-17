# import module
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Настройки среды
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

#Путь к файлу-источнику
full_dis = "C:/py_app/dis/15022022_11.20.xlsx"

@st.cache
def load_dataset(data_link):
    dataset = pd.read_excel(data_link)
    return dataset

@st.cache
def load_excel(data_link, sheet, col_name):
    dataset = pd.read_excel(data_link,sheet, index_col=False,usecols=col_name)
    return dataset

@st.cache
def load_stantion():# Загрузка списка станций назначения
    full_data=load_excel(full_dis, 'tmp', "Z")#загрузка списка станций назначения
    df = pd.DataFrame(full_data,index=None, columns=None)
    val=df.drop_duplicates()
    return val

@st.cache
def load_type_vag():# Загрузка типов вагонов
    full_data=load_excel(full_dis, 'tmp', "M")#загрузка списка типов вагонов
    df = pd.DataFrame(full_data,index=None, columns=None)
    val=df.drop_duplicates()
    return val

@st.cache
def load_factory():# Загрузка типов вагонов
    full_data=load_excel(full_dis, 'tmp', "I")#загрузка списка типов вагонов
    df = pd.DataFrame(full_data,index=None, columns=None)
    val=df.drop_duplicates()
    return val

# Header
st.title("Дислокация ПС с готовой продукции", anchor='dislocation')

s_bar=st.sidebar
s_bar.title("Настройки:")

version_disl = s_bar.selectbox( "Версия дислокации: " ,
[ '15.02.2022 16:18' , '12.01.2022 05:00' , '15.01.2022 08:00', '19.01.2022 05:00' ])

ls=load_stantion()# получение списка всех существующих станций назначения
stantion = s_bar.multiselect(label='Станции назначения: ', options=ls.sort_values(by="destination_station", ascending=True), default=None)

s_bar.button( "Сохранить настройки и обновить данные" )

fac=load_factory()
fc = s_bar.multiselect(label='Заводы: ', options=fac.sort_values(by="factory", ascending=True), default=list(fac['factory']))

type_vag=load_type_vag()
tv = s_bar.multiselect(label='Типы вагонов: ', options=type_vag.sort_values(by="Vagon_type", ascending=True), default=list(type_vag['Vagon_type']))

if len(stantion) == 0:
    #Загружаем список по заводам и вычисляем сумму в разрезе заводв
    volume_data = load_excel(full_dis, 'tmp', "I, AE, Z, M")
    volume_data=volume_data[(volume_data.destination_station.isin(list(ls['destination_station']))) & (volume_data.factory.isin(fc)) & (volume_data.Vagon_type.isin(tv))]
    volume_data=volume_data.groupby(['factory']).sum()
    volume_data=volume_data.reset_index()#сброс индексного поля возникающего при группировке
    sum_vol=volume_data['Volume_tn'].sum()
    
    #Загружаем список по типам вагонов и вычисляем сумму в разрезе типов вагонов
    vag_data = load_excel(full_dis, 'tmp', "I, AE, Z, M")
    vag_data=vag_data[(vag_data.destination_station.isin(list(ls['destination_station']))) &(vag_data.factory.isin(fc)) & (vag_data.Vagon_type.isin(tv))]
    vag_data=vag_data.groupby(['Vagon_type']).sum()
    vag_data=vag_data.reset_index()#сброс индексного поля возникающего при группировке

    #Загружаем объемы в разрезе станций назначения
    vol_data_dest = load_excel(full_dis, 'tmp', "I, AE, Z, M")
    vol_data_dest=vol_data_dest[(vol_data_dest.factory.isin(fc)) & (vol_data_dest.Vagon_type.isin(tv))]
    vol_data_dest=vol_data_dest.groupby(['destination_station']).sum()
    vol_data_dest=vol_data_dest.reset_index()#сброс индексного поля возникающего при группировке
    
    #Загружаем брошенные
    vol_ab = load_excel(full_dis, 'tmp', "I,F,AE,Z,M")
    vol_ab=vol_ab[(vol_ab.Operation=="БРОС") & (vol_ab.destination_station.isin(list(ls['destination_station']))) & (vol_ab.factory.isin(fc)) & (vol_ab.Vagon_type.isin(tv))]
    sum_vol_ab=vol_ab['Volume_tn'].sum()

else:
    #Загружаем список по заводам и вычисляем сумму в разрезе заводв
    volume_data = load_excel(full_dis, 'tmp', "I, AE, Z, M")
    volume_data=volume_data[(volume_data.destination_station.isin(stantion)) & (volume_data.factory.isin(fc)) & (volume_data.Vagon_type.isin(tv))]
    volume_data=volume_data.groupby(['factory']).sum()
    volume_data=volume_data.reset_index()#сброс индексного поля возникающего при группировке
    sum_vol=volume_data['Volume_tn'].sum()

    #Загружаем список по типам вагонов и вычисляем сумму в разрезе типов вагонов
    vag_data = load_excel(full_dis, 'tmp', "I, AE, Z, M")
    vag_data=vag_data[(vag_data.destination_station.isin(stantion)) & (vag_data.factory.isin(fc)) & (vag_data.Vagon_type.isin(tv))]
    vag_data=vag_data.groupby(['Vagon_type']).sum()
    vag_data=vag_data.reset_index()#сброс индексного поля возникающего при группировке

    #Загружаем объемы в разрезе станций назначения
    vol_data_dest = load_excel(full_dis, 'tmp', "I, AE, Z, M")
    vol_data_dest=vol_data_dest[(vol_data_dest.destination_station.isin(stantion)) & (vol_data_dest.factory.isin(fc)) & (vol_data_dest.Vagon_type.isin(tv))]
    vol_data_dest=vol_data_dest.groupby(['destination_station']).sum()
    vol_data_dest=vol_data_dest.reset_index()#сброс индексного поля возникающего при группировке
    
    #Загружаем брошенные
    vol_ab = load_excel(full_dis, 'tmp', "I,F,AE,Z,M")
    vol_ab=vol_ab[(vol_ab.Operation=="БРОС") & (vol_ab.destination_station.isin(stantion)) & (vol_ab.factory.isin(fc)) & (vol_ab.Vagon_type.isin(tv))]
    sum_vol_ab=vol_ab['Volume_tn'].sum()


col3, col4 = st.columns(2)
col3.metric("Всего в пути:", str(round(sum_vol,2)) + " тн", "")
col4.metric("в том числе в брошенном ПС:", str(round(sum_vol_ab,2)) + " тн", "")


st.write("______________________________________________________________________________________________")

col1, col2, = st.columns(2)
with col1:
    st.subheader("Объем в пути в разрезе заводов,тн")
    bar1 = alt.Chart(volume_data).mark_bar().encode(
    alt.X("Volume_tn:Q", title=None),alt.Y("factory", title=None),tooltip=["Volume_tn"]).properties(width=650,height=250).configure_view(strokeWidth=0)
    st.altair_chart(bar1)
with col2:
    st.subheader("Объем в пути по типам вагонов, тн.")    
    bar2 = alt.Chart(vag_data).mark_bar().encode(
    alt.X('Volume_tn:Q', title=None),
    alt.Y('Vagon_type',title=None),tooltip=["Volume_tn"]).properties(width=650,height=250).configure_view(strokeWidth=0)
    st.altair_chart(bar2)

st.subheader("Объем в пути по станциям назначения, тн")    
scales = alt.selection_interval(bind='scales')

if len(stantion) == 0:
    bar3 = alt.Chart(vol_data_dest).mark_bar(size=20,color="green").encode(
    alt.X('destination_station', title=None, sort=alt.SortField(field="Volume_tn",order='descending')),
    alt.Y('Volume_tn',title=None),tooltip=["Volume_tn","destination_station"]).properties(width=1450,height=450).configure_view(strokeWidth=0).add_selection(scales)
    st.altair_chart(bar3)

    st.subheader("Прогноз прибытия на выбранную станцию назначения,тн")
    option_2 = st.selectbox(
    label='Выберите станцию назначения для просмотра прогноза подхода вагонов:',options=ls.sort_values(by="destination_station", ascending=True))
else:
    bar3 = alt.Chart(vol_data_dest).mark_bar(size=20,color="green").encode(
    alt.X('destination_station', title=None, sort=alt.SortField(field="Volume_tn",order='descending')),
    alt.Y('Volume_tn',title=None),tooltip=["Volume_tn","destination_station"]).properties(width=1450,height=450).configure_view(strokeWidth=0).add_selection(scales)
    st.altair_chart(bar3)

    st.subheader("Прогноз прибытия на выбранную станцию назначения,тн")
    option_2 = st.selectbox(
    label='Выберите станцию назначения для просмотра прогноза подхода вагонов:',options=stantion)
    

#******************************************************************************************
#Загружаем Прогноз по выбранной станции
Forecast_vol = load_excel(full_dis, 'tmp', "I,M,Z,AE,HR")
Forecast_vol=Forecast_vol[(Forecast_vol.destination_station==option_2) & (Forecast_vol.factory.isin(fc)) & (Forecast_vol.Vagon_type.isin(tv))]
Forecast_vol=Forecast_vol.groupby(['Forecast']).sum()
Forecast_vol=Forecast_vol.reset_index()#сброс индексного поля возникающего при группировке
Forecast_vol['Forecast']=Forecast_vol['Forecast'].dt.tz_localize(tz='Europe/Moscow')

brush = alt.selection(type='interval', encodings=['x'])
bar3 = alt.Chart(Forecast_vol).mark_bar(size=30,color="red").encode(
alt.X('Forecast:T', title=None,scale=alt.Scale(nice={'interval': 'day', 'step': 1}),axis=alt.Axis(format="%d %m %y")),
alt.Y('Volume_tn:Q',title=None),tooltip=["Volume_tn","Forecast"]
).properties(width=1450,height=300).configure_view(strokeWidth=0)

st.altair_chart(bar3)
st.write("Посуточный прогноз подхода на выбранную станцию:")
st.write(Forecast_vol)#Таблица

#******************************************************************************************
st.write("______________________________________________________________________________________________")
st.subheader("Повагонка:")
all_data=load_excel(full_dis, 'tmp', "C,E,G,I,J,L,M,Z,AC,AD,AE,AN,AT,EJ,HR")#загрузка общей таблицы данных
all_data_1=all_data[(all_data.destination_station==option_2) & (all_data.factory.isin(fc)) & (all_data.Vagon_type.isin(tv))]
st.write(all_data_1)



#******************************************************************************************
#with col3:
#    st.caption("Объем в брошенных вагонах")
#    bar = alt.Chart(ab_vag_data).mark_bar().encode(
#    alt.X('volume',scale=alt.Scale(domain=(0,100))),
#    y='type_vag',
#    color=alt.condition(pts, alt.ColorValue("steelblue"), alt.ColorValue("grey"))
#    ).properties(
#    width=450,
#    height=500
#    ).add_selection(pts)
#    st.altair_chart(bar)
#    #sns.catplot(x="volume", y="type_vag", kind="bar", data=ab_vag_data, palette="rocket")
#    #st.pyplot()
