import streamlit as st
import os
from PIL import Image
from simpledatabase import SimpleDatabase
from face_clustering import FaceClustering

def tag_people(selected_folder):
    db = SimpleDatabase()
    fc = FaceClustering(selected_folder)
    
    if not fc.is_clustered():
        st.error("Please cluster the images first.")
        return

    clusters = fc.get_clusters()
    
    for cluster_id, images in clusters.items():
        if images:
            st.subheader(f"Cluster {cluster_id}")
            img = Image.open(images[0])
            st.image(img, width=200)
            name = st.text_input(f"Name for Cluster {cluster_id}")
            
            if name:
                db.save_tag(cluster_id, name, images)

    if st.button("Save Tags"):
        st.success("Tags saved successfully!")
