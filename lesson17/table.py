import streamlit as st

tab1,tab2,tab3, = st.tabs(["tab 1","tab 2","tab 3"])


with tab1:
    st.header("cotent for tab 1 ")
    st.write("thisis the content of the first tab")


with tab2:
    st.header("cotent for tab 2 ")
    st.write("thisis the content of the first tab")


with tab3:
    st.header("cotent for tab 3")
    st.write("thisis the content of the first tab")