import streamlit as st
c = st.container()
st.header('Hello! This is MPG ↔ KPL Program')
if st.button('Nice to meet you'):
    st.write('Nice to meet you too')
    
st.header('MPG(Miles per Gallon) -> KPL(Kilometers per Liter)')
st.subheader('MPG')
MPG = st.slider('MPG를 입력하세요', min_value=0.0, max_value=50.0, value=25.6, step=0.1)
KPL = MPG * 1.60934 / 3.78541
st.write(f'KPL은 {KPL} 입니다.')

st.header('KPL(Kilometers per Liter) -> MPG(Miles per Gallon)')
st.subheader('KPL')
kpl = st.slider('KPL을 입력하세요', min_value=0.0, max_value=30.0, value=10.6, step=0.1)
mpg = kpl * 3.78541 / 1.60934
st.write(f'MPG은 {mpg} 입니다.')

st.write('Thank you for using our service.')
