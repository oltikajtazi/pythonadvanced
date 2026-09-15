import pandas as pd
import  streamlit as st



books_df= pd.read_csv("dat.csv")


#Streamlit app title

st.title("bestselling books")
st.title("this ap analyzes the amazon yop edfnhdofjs")

st.sidebar.header("add new book Data")

with st.sidebar.form("book_form"):
    new_name= st.text_input("Book name")
    new_author = st.text_input("Author")
    new_user_rating = st.slider("User Rating", 0.0, 5.0,0.0,0.1)
    new_reviews = st.number_input("reviews", min_value=0,step=1)
    new_price= st.number_input("Price",min_value=0,step=1)
    new_year = st.number_input("Price", min_value=2009, step=1)
    new_genre=st.selectbox("Genre",books_df['Genre'].unique())
    submit_button=st.form_submit_button (label="add book")


if submit_button:
    new_data={
        'Name': new_name,
        'Author':new_author,
        'User Rating':new_reviews,
        'Price':new_price,
        'Year':new_year,
        'Genre':new_genre,
    }

    books_df = pd.concat([pd.DataFrame(new_data,index=[0]),books_df],ignore_index=True)
    books_df.to_csv("dat.csv",index=False)




