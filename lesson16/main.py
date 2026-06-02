import streamlit as st

def main():
    st.title("hello worl")

    st.button("click me")

st.checkbox("olti")

if st.checkbox("nili"):
    st.write("qiky tekst po shfaqet sepse ti eke check katrorin e zbrazet")



if st.button("click") :
    st.write("button clicke3d")


name = st.text_input("Enter your name")
st.write("your name is", name)

age = st.number_input("enter your age:", min_value=0, max_value=155)
st.write("your age is", age)

message = st.text_area("enter your mesage")

if st.button("succses"):
    st.success("operating was successful")



if __name__ =="__main__":
    main()
