import streamlit as st
from simpledatabase import SimpleDatabase
from sidebar_and_gallery import start_app

# Initialize the database
db = SimpleDatabase()

def set_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            color: #000000;
        }
        .stButton > button {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True
    )

def user_exists(email, password):
    user = db.users_df[db.users_df['email'] == email]
    if not user.empty and str(user.iloc[0]['password']) == password:
        return True
    return False

def add_data(username, email, password):
    db.add_user(username, password, email)

def login():
    set_custom_style()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        start_app()
    else:
        st.title("Jupyter Photo Cloud")
        
        choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])
        
        if choice == 'Login':
            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')

            if st.button('Login'):
                if user_exists(email, password):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials or account doesn't exist. Please sign up first.")

        elif choice == 'Sign Up':
            username = st.text_input('Enter your Username')
            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')

            if st.button('Create my Account!'):
                add_data(username, email, password)
                st.session_state.logged_in = True
                st.rerun()

if __name__ == '__main__':
    login()
