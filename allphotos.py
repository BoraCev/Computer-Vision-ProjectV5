import streamlit as st
import os
from PIL import Image
from simpledatabase import SimpleDatabase

def display_all_photos():
    st.title("All Photos")

    db = SimpleDatabase()
    all_images = db.get_all_images()

    if all_images:
        st.write(f"Total unique photos: {len(all_images)}")
        
        cols = st.columns(4)
        for idx, image_path in enumerate(all_images):
            if os.path.exists(image_path):
                with cols[idx % 4]:
                    img = Image.open(image_path)
                    img.thumbnail((200, 200))
                    st.image(img, use_column_width=True)
    else:
        st.write("No photos found.")

def show_all_photos_page():
    display_all_photos()

if __name__ == "__main__":
    show_all_photos_page()
