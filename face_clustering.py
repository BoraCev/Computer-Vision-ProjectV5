import face_recognition
import numpy as np
from PIL import Image, ImageDraw
import os
import streamlit as st
import hdbscan
import time
import json

class FaceClustering:
    def __init__(self, image_folder, encoding_file='face_encodings.json'):
        self.image_folder = image_folder
        self.images = self.load_images()
        self.all_face_encodings = []
        self.all_face_locations = []
        self.image_paths = []
        self.encoding_file = encoding_file
        self.saved_encodings = self.load_saved_encodings()
        self.labels_ = None

    def load_images(self):
        image_paths = []
        for f in os.listdir(self.image_folder):
            if f.endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(self.image_folder, f)
                image_paths.append(full_path)
        return image_paths

    def load_saved_encodings(self):
        if os.path.exists(self.encoding_file):
            with open(self.encoding_file, 'r') as f:
                return json.load(f)
        return {}

    def save_encodings(self):
        with open(self.encoding_file, 'w') as f:
            json.dump(self.saved_encodings, f)

    def extract_faces_and_features(self):
        image_placeholder = st.empty()

        for image_path in self.images:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            pil_image = Image.fromarray(image)
            draw = ImageDraw.Draw(pil_image)

            for (top, right, bottom, left) in face_locations:
                draw.rectangle(((left, top), (right, bottom)), outline="red", width=5)

            image_placeholder.image(pil_image, caption=f"Processing {os.path.basename(image_path)}", use_column_width=True)

            face_encodings = face_recognition.face_encodings(image, face_locations)
            self.all_face_encodings.extend(face_encodings)
            self.all_face_locations.extend(face_locations)
            self.image_paths.extend([image_path] * len(face_encodings))

            time.sleep(0.2)
            
        image_placeholder.markdown('')

    def cluster_faces(self):
        if self.all_face_encodings:
            clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
            self.labels_ = clusterer.fit_predict(self.all_face_encodings)
            return self.labels_
        return []

    def display_clustered_faces(self, labels):
        clustered_images = {}
        for label, image_path, location in zip(labels, self.image_paths, self.all_face_locations):
            if label not in clustered_images:
                clustered_images[label] = [(image_path, location)]
            else:
                clustered_images[label].append((image_path, location))
        
        if 'cluster_names' not in st.session_state:
            st.session_state.cluster_names = {}

        with st.form("cluster_naming_form"):
            for label, images in clustered_images.items():
                if label == -1:
                    continue
                st.markdown(f"### Cluster {label}")
                name = st.text_input(f'Name for Cluster {label}', key=f'name_{label}', value=st.session_state.cluster_names.get(str(label), ''))
                st.session_state.cluster_names[str(label)] = name
                cols = st.columns(3)
                for index, (image_path, location) in enumerate(images):
                    with cols[index % 3]:
                        image = Image.open(image_path)
                        draw = ImageDraw.Draw(image)
                        top, right, bottom, left = location
                        draw.rectangle(((left, top), (right, bottom)), outline="red", width=5)
                        st.image(image, caption=os.path.basename(image_path), use_column_width=True)
            
            submit_button = st.form_submit_button("Save Cluster Names")
            if submit_button:
                self.save_cluster_names(st.session_state.cluster_names, labels)
                st.session_state.clustering_complete = False

    def save_cluster_names(self, cluster_names, labels):
        for label, name in cluster_names.items():
            if name:
                encodings = [self.all_face_encodings[i].tolist() for i, lbl in enumerate(labels) if str(lbl) == label]
                self.saved_encodings[name] = encodings
        self.save_encodings()
        st.success("Cluster names saved successfully!")

    def load_cluster_names(self):
        return {name: np.array(encodings) for name, encodings in self.saved_encodings.items()}

    def is_clustered(self):
        return self.labels_ is not None

    def get_clusters(self):
        if not self.is_clustered():
            return {}
        
        clustered_images = {}
        for label, image_path in zip(self.labels_, self.image_paths):
            if label not in clustered_images:
                clustered_images[label] = [image_path]
            else:
                clustered_images[label].append(image_path)
        return clustered_images

    def run(self):
        if 'clustering_complete' not in st.session_state:
            st.session_state.clustering_complete = False

        if not st.session_state.clustering_complete:
            if not self.images:
                st.write("No images found in the specified folder.")
                return
            
            with st.spinner('Extracting faces and features...'):
                self.extract_faces_and_features()
            
            with st.spinner('Clustering faces...'):
                st.session_state.labels = self.cluster_faces()
                if st.session_state.labels is None or len(set(st.session_state.labels)) == 1 and -1 in st.session_state.labels:
                    st.write("No faces found for clustering or all faces are marked as noise.")
                    return
            
            st.session_state.clustering_complete = True

        self.display_clustered_faces(st.session_state.labels)
