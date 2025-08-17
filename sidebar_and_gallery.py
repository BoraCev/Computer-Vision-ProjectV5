import streamlit as st
import os
from PIL import Image
from chat_page import upload_file
from face_clustering import FaceClustering
import numpy as np
import face_recognition
from tagging import tag_people
from allphotos import show_all_photos_page

image_folder = r'test_images'

def set_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .stSidebar {
            background-color: #2c3e50;
            padding-top: 2rem;
        }
        .stButton > button {
            height: 3rem;
            width: 100%;
            font-size: 1rem;
            font-weight: bold;
            margin: 0.5rem 0;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stSelectbox {
            margin-bottom: 1rem;
        }
        .stTab {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .stHeader {
            color: #3498db;
            font-weight: bold;
        }
        .stImage {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .stImage:hover {
            transform: scale(1.05);
        }
        .gallery-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }
        .gallery-item {
            margin: 10px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True
    )

def start_app():
    set_custom_style()
    
    st.sidebar.title("Navigation")
    
    menu_items = {
        "Home": "Home",
        "Galleries": "Galleries",
        "Manage Images": "Manage",
        "All Photos": "All Photos"
    }
    
    choice = st.sidebar.radio("Go to", list(menu_items.keys()))
    st.session_state.page = menu_items[choice]

    if st.session_state.page == "Home":
        st.title("Welcome to Jupyter Photo Cloud")
        st.markdown("### Your personal photo management solution")
        upload_file()

    elif st.session_state.page == "Manage":
        image_folder = r'galleries'

        if os.path.isdir(image_folder):
            gallery_list = ['Choose a Gallery'] + [name for name in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder, name))]
        else:
            st.error("Image folder not specified or does not exist.")

        tab1, tab2, tab3 = st.tabs(["Upload Images", "Cluster Images", "Tag People"])

        with tab1:
            st.header("Upload Images to Gallery")
            choice = st.selectbox('Select Gallery', gallery_list, key='upload_gallery')
            if choice != 'Choose a Gallery':
                selected_folder = os.path.join(image_folder, choice)
                
                uploaded_files = st.file_uploader("Choose files to upload", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
                if st.button("Upload") and uploaded_files is not None:
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(selected_folder, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    st.success(f"Photos were uploaded into the gallery '{choice}'.")

                if os.path.isdir(selected_folder):
                    images = [os.path.join(selected_folder, f) for f in os.listdir(selected_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
                    
                    if images:
                        st.subheader("Gallery Preview")
                        st.markdown('<div class="gallery-container">', unsafe_allow_html=True)
                        for image_path in images[:9]:  # Show up to 9 images
                            img = Image.open(image_path)
                            st.markdown(f'<div class="gallery-item"><img src="data:image/png;base64,{image_to_base64(img)}" width="200"></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"No images found in '{choice}' Gallery.")
            else:
                st.warning("Please select a gallery before uploading images.")

        with tab2:
            st.header("Cluster Images")
            choice = st.selectbox('Select Gallery for Clustering', gallery_list, key='cluster_gallery')
            if choice != 'Choose a Gallery':
                selected_folder2 = os.path.join(image_folder, choice)
                if st.button('Start Clustering'):
                    with st.spinner("Clustering in progress..."):
                        face_clustering = FaceClustering(selected_folder2)
                        face_clustering.run()
            else:
                st.warning("Please select a gallery before clustering.")

        with tab3:
            st.header("Tag People")
            choice = st.selectbox('Select Gallery for Tagging', gallery_list, key='tag_gallery')
            if choice != 'Choose a Gallery':
                selected_folder = os.path.join(image_folder, choice)
                fc = FaceClustering(selected_folder)
                
                if fc.is_clustered():
                    if st.button('Start Tagging'):
                        tag_people(selected_folder)
                else:
                    st.warning("Please cluster the images first.")
                    if st.button('Cluster Images'):
                        fc.run()
                        st.success("Clustering complete. You can now start tagging.")
            else:
                st.warning("Please select a gallery before tagging.")

    elif st.session_state.page == "Galleries":
        st.title("Manage Galleries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Create a New Gallery")
            gallery_name_input = st.text_input('Gallery Name')
            
            def create_gallery():
                if gallery_name_input:
                    try:
                        os.mkdir(os.path.join(r'galleries', gallery_name_input))
                        st.success(f'Gallery "{gallery_name_input}" created successfully!')
                    except OSError as e:
                        st.error(f'Failed to create gallery: {e}')
            
            if st.button('Create Gallery'):
                create_gallery()
                st.rerun()

        with col2:
            st.subheader("Existing Galleries")
            image_folder = r'galleries'
            if os.path.isdir(image_folder):
                subfolders = [os.path.join(image_folder, name) for name in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder, name))]

                for folder in subfolders:
                    if st.button(f'View {os.path.basename(folder)}'):
                        st.session_state.view_gallery = folder
                        st.rerun()

            if 'view_gallery' in st.session_state:
                st.title(f"Viewing Gallery: {os.path.basename(st.session_state.view_gallery)}")
                images = [f for f in os.listdir(st.session_state.view_gallery) if f.endswith(('.png', '.jpg', '.jpeg'))]
                
                st.markdown('<div class="gallery-container">', unsafe_allow_html=True)
                for image in images:
                    img = Image.open(os.path.join(st.session_state.view_gallery, image))
                    st.markdown(f'<div class="gallery-item"><img src="data:image/png;base64,{image_to_base64(img)}" width="200"></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button('Close Gallery'):
                    del st.session_state.view_gallery
                    st.rerun()
        
        if not os.path.isdir(image_folder):
            st.error("Image folder not specified or does not exist.")

    elif st.session_state.page == "All Photos":
        show_all_photos_page()

def image_to_base64(image):
    import io
    import base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
