import streamlit as st
import os
from PIL import Image

image_folder = 'test_images'  # Set the image folder path


def start_app():
    st.title("Jupyter Photo Cloud App")  # Set the app title
    
    # Create two tabs: one for the Image Gallery and one for People
    tab1, tab2 = st.tabs(["Image Gallery", "People"])

    # Image Gallery tab
    with tab1:
        # Check if the image folder is specified
        if image_folder:
            # Get the paths of all images in the folder
            images = []  # Create an empty list to store image paths
            for f in os.listdir(image_folder):  # Loop through each file in the folder
                if f.endswith(('.png', '.jpg', '.jpeg')):  # Check if the file has an image extension
                    full_path = os.path.join(image_folder, f)  # Create the full file path
                    images.append(full_path)  # Add the file path to the list
                    st.rerun()
            # If there are images, display them in two columns
            if images:
                with st.container(height=600):
                    cols = st.columns(2)  # Create two columns
                    for index, image_path in enumerate(images):
                        with cols[index % 2]:  # Alternate between the two columns
                            img = Image.open(image_path)  # Open the image
                            st.image(img, caption=os.path.basename(image_path), use_column_width=True)  # Display the image
                            st.rerun()
            else:
                st.write("No images found in the specified folder.")  # Show message if no images are found
        else:
            st.write("Image folder not specified in the configuration file.")  # Show message if image folder is not specified
    
    # People tab
    with tab2:
        st.markdown("Click the button below to start clustering.")  # Provide instructions for this tab
        st.button('Start Clustering')  # Button to initiate clustering

# Ensure the app only runs when this script is executed directly

