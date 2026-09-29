import streamlit as st
import requests
import pandas as pd

st.title("Project managemet App")

st.header("add a Developer")
dev_name=st.text_input("deleloper Name")
dev_experience = st.number_input("Experience (Years)",min_value=0,max_value=50,value=0)


if st.button("Creat Developer"):
    dev_data={"name":dev_name,"experience":dev_experience}
    response = requests.post("http://localhost:8000/developers", json=dev_data)
    st.header("add a project")

proj_title = st.text_input("project title")
proj_desc = st.text_input("project description")
proj_langs = st.text_input("Langues Used (Coma-separeted)")
lead_dev_name = st.text_input("Developer name")



if st.button("Creat Developer"):
    lead_dev_data={"name":dev_name,"experience":dev_experience}
    proj_data={
        "title":proj_title,
        "description":proj_desc,
        "languages":proj_langs.split(","),
        "lead_developer":lead_dev_data

    }





























