import streamlit as st

st.title("BMI Calculator")

name = st.text_input("Name")
age = st.number_input("Age", min_value=1)
weight = st.number_input("Weight (kg)", min_value=1.0)
height = st.number_input("Height (m)", min_value=0.1)

if st.button("Calculate"):
    bmi = weight / (height ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    st.write(f"Name: {name}")
    st.write(f"Age: {age}")
    st.write(f"BMI: {bmi:.2f}")
    st.write(f"Category: {category}")