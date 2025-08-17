import pandas as pd
import streamlit as st
from simpledatabase import SimpleDatabase
from PIL import Image

def upload_file():
    db = SimpleDatabase()

    st.title("Chat BOT")
    st.success("Logged in!")
    
    user_input = st.text_input("Enter a name to search for:")
    if user_input:
        images = db.get_images_by_name(user_input)
        if images:
            for img_path in images:
                st.image(Image.open(img_path), width=200)
        else:
            st.write("No images found for this name.")
