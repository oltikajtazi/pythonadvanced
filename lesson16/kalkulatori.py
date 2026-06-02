import streamlit as st

def kalkulo(num1,num2,operation):
    if operation=="mbledhja":
        result = num1+num2
    elif  operation == "zbritja":
            result = num1 - num2

    return   result



st.title("simple calculator")


num1 = st.number_input("enter the fist number", step=1)
num2 = st.number_input("enter the second number", step=1)

operation = st.radio("select operation",["mbledhja","zbritja"])

result = kalkulo(num1,num2,operation)

st.write(result)