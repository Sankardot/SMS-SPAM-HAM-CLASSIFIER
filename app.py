import streamlit as st
import json
import pickle
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# File path for storing user data
user_file_path = "users.json"

# Load users from JSON file
def load_users():
    try:
        with open(user_file_path, "r") as file:
            # Read the file content and check if it's empty
            file_content = file.read().strip()
            if not file_content:
                return {}
            return json.loads(file_content)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        st.error(f"Error loading user data: {e}")
        return {}

# Save users to JSON file
def save_users(users):
    try:
        with open(user_file_path, "w") as file:
            json.dump(users, file)
    except Exception as e:
        st.error(f"Error saving user data: {e}")

# Initialize users data
users = load_users()

# Handle user login
def login(username, password):
    if username in users and users[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.username = username  # Store the username
        st.success(f"Logged in successfully! Welcome back, {username}!")
    else:
        st.error("Invalid username or password")

# Handle user registration
def register(username, password, email, dob, phone_number):
    if username in users:
        st.error("Username already exists!")
    else:
        users[username] = {
            "password": password,
            "email": email,
            "dob": dob,
            "phone_number": phone_number
        }
        save_users(users)
        st.success("User registered successfully! Please login.")

# Handle password reset
def reset_password(email, new_password):
    for username, data in users.items():
        if data["email"] == email:
            users[username]["password"] = new_password
            save_users(users)
            st.success("Your password has been successfully reset!")
            return
    st.error("No account associated with this email address.")

# Function to log out
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""  # Clear the username from session state

# Spam classifier
def spam_checker():
    st.title("📧 EMAIL/SMS Spam Classifier")

    ps = PorterStemmer()

    def transform_mails(mails):
        mails = mails.lower()
        mails = nltk.word_tokenize(mails)

        y = []
        for i in mails:
            if i.isalnum():
                y.append(i)

        mails = y[:]
        y.clear()

        for i in mails:
            if i not in stopwords.words('english') and i not in string.punctuation:
                y.append(i)

        mails = y[:]
        y.clear()

        for i in mails:
            y.append(ps.stem(i))

        return " ".join(y)

    tfidf = pickle.load(open(r"C:\Users\hp\Desktop\project\vectorizer.pkl", 'rb'))
    model = pickle.load(open(r"C:\Users\hp\Desktop\project\model.pkl", 'rb'))

    input_msg = st.text_area("💬 Enter your text message here", height=150)

    if st.button('🔍 Predict'):
        transformed_msg = transform_mails(input_msg)
        vector_msg = tfidf.transform([transformed_msg])
        result = model.predict(vector_msg)[0]

        if result == 1:
            st.markdown("<h2 style='color: red;'>🚨 This is SPAM</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color: green;'>✅ This is NOT SPAM</h2>", unsafe_allow_html=True)

# Apply dynamic background color
def apply_background_color(color, text_color="#FFFFFF"):
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {color};
            }}
            .stText, .stMarkdown {{
                color: {text_color};
            }}
            /* Custom CSS to style the input fields */
            .stTextInput input {{
                background-color: white;
                color: black;
            }}
            .stTextInput label {{
                color: white;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Main app logic
if not st.session_state.authenticated:
    # Apply the background color used in the login page (e.g., #2E2E2E, a dark gray color)
    apply_background_color("#2E2E2E", "#FFFFFF")  # Dark gray background with white text
    st.markdown("<h1 class='stTitle' style='color: white; font-weight: bold;'>🔒 Welcome to the Spam Classifier App</h1>", unsafe_allow_html=True)
    choice = st.sidebar.radio("Choose an option", ["Login", "Register", "Forgot Password"])

    if choice == "Login":
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: white;'>Login</h2>", unsafe_allow_html=True)  # Use st.markdown for custom styling
        
        # Custom styles for the text input fields
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            login(username, password)
        
        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "Register":
        st.markdown("<div class='main-container register-page'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: white;'>Register</h2>", unsafe_allow_html=True)  # Use st.markdown for custom styling
        st.markdown("<p style='color: white;'>Please fill in the details to create an account.</p>", unsafe_allow_html=True)

        # Collect registration details with custom heading styles
        st.markdown("<p style='color: white;'>Choose a username</p>", unsafe_allow_html=True)
        username = st.text_input("", key="register_username")
        
        st.markdown("<p style='color: white;'>Choose a password</p>", unsafe_allow_html=True)
        password = st.text_input("", type="password", key="register_password")
        
        st.markdown("<p style='color: white;'>Enter your email</p>", unsafe_allow_html=True)
        email = st.text_input("", key="register_email")
        
        st.markdown("<p style='color: white;'>Enter your date of birth</p>", unsafe_allow_html=True)
        dob = st.date_input("", key="register_dob")
        
        st.markdown("<p style='color: white;'>Enter your phone number</p>", unsafe_allow_html=True)
        phone_number = st.text_input("", key="register_phone_number")

        if st.button("Register", key="register_button"):
            if username and password and email and dob and phone_number:
                register(username, password, email, str(dob), phone_number)
            else:
                st.error("All fields are required!")

        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "Forgot Password":
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: white;'>Forgot Password</h2>", unsafe_allow_html=True)

        email = st.text_input("Enter your email address to reset your password")
        new_password = st.text_input("Enter your new password", type="password")

        if st.button("Reset Password"):
            if email and new_password:
                reset_password(email, new_password)
            else:
                st.error("Please provide both email and new password.")

        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Greet the user after successful login
    st.markdown(f"<h1 style='color: black;'>Hi, {st.session_state.username}!</h1>", unsafe_allow_html=True)
    apply_background_color("#e0f7fa")  # Light blue for Spam Checker page
    # Sidebar logout button
    st.sidebar.button("Logout", on_click=logout)
    spam_checker()
