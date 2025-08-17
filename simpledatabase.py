import pandas as pd
from datetime import datetime
import os

class SimpleDatabase:
    def __init__(self, users_csv='users.csv', settings_csv='settings.csv', images_csv='images.csv'):
        self.users_csv = users_csv
        self.settings_csv = settings_csv
        self.images_csv = images_csv
        self._initialize_files()

    def _initialize_files(self):
        # Initialize users table
        try:
            self.users_df = pd.read_csv(self.users_csv)
        except FileNotFoundError:
            self.users_df = pd.DataFrame(columns=['username', 'password', 'email', 'date_created'])
            self.users_df.to_csv(self.users_csv, index=False)

        # Initialize settings table
        try:
            self.settings_df = pd.read_csv(self.settings_csv)
        except FileNotFoundError:
            self.settings_df = pd.DataFrame(columns=['username', 'folder_location'])
            self.settings_df.to_csv(self.settings_csv, index=False)

        # Initialize images table
        try:
            self.images_df = pd.read_csv(self.images_csv)
        except FileNotFoundError:
            self.images_df = pd.DataFrame(columns=['username', 'image_id', 'tag', 'image_location'])
            self.images_df.to_csv(self.images_csv, index=False)

    def add_user(self, username, password, email):
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_user = pd.DataFrame([{'username': username, 'password': password, 'email': email, 'date_created': date_created}])
        self.users_df = pd.concat([self.users_df, new_user], ignore_index=True)
        self.users_df.to_csv(self.users_csv, index=False)

    def add_user_setting(self, username, folder_location):
        new_setting = pd.DataFrame([{'username': username, 'folder_location': folder_location}])
        self.settings_df = pd.concat([self.settings_df, new_setting], ignore_index=True)
        self.settings_df.to_csv(self.settings_csv, index=False)

    def add_image(self, username, image_id, tag, image_location):
        full_path = os.path.abspath(image_location)
        new_image = pd.DataFrame([{'username': username, 'image_id': image_id, 'tag': tag, 'image_location': full_path}])
        self.images_df = pd.concat([self.images_df, new_image], ignore_index=True)
        self.images_df.to_csv(self.images_csv, index=False)

    def get_user(self, username):
        return self.users_df[self.users_df['username'] == username]

    def get_user_settings(self, username):
        return self.settings_df[self.settings_df['username'] == username]

    def get_user_images(self, username):
        return self.images_df[self.images_df['username'] == username]

    def get_all_images(self):
        return self.images_df['image_location'].unique().tolist()

    def save_tag(self, cluster_id, name, images):
        for image_path in images:
            new_tag = pd.DataFrame([{'username': 'current_user', 'image_id': cluster_id, 'tag': name, 'image_location': image_path}])
            self.images_df = pd.concat([self.images_df, new_tag], ignore_index=True)
        self.images_df.to_csv(self.images_csv, index=False)

    def get_images_by_name(self, name):
        return self.images_df[self.images_df['tag'] == name]['image_location'].tolist()
