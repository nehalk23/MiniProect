import streamlit as st
import re
import socket
import smtplib
from email.message import EmailMessage
import ssl
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import subprocess

# Function to verify if an email address is valid
def verify_email(email):
    pattern = r'^\w+([\.-]?\w+)@\w+([\.-]?\w+)(\.\w{2,3})+$'
    return re.match(pattern, email) is not None

# Function to find IP address from a given domain
def find_ip_address(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

# Function to block IP address using iptables
def block_ip(ip_address):
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"])

def unblock_ip(ip_address):
    subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip_address, "-j", "DROP"])

def send_mail(sender_email, receiver_email, password, message, smtp_server="smtp.gmail.com"):
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, 587)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        server.quit()

# Load the model and vectorizer
with open('spam.pkl', 'rb') as f:
    model = pickle.load(f)

with open('vectorizer.pkl', 'rb') as f:
    cv = pickle.load(f)

# Function to predict if an email is spam or not
def predict_spam(email):
    email_vectorized = cv.transform([email])
    return model.predict(email_vectorized)[0]

def main():
    st.set_page_config(page_title="Email Spam Detection & IP Blocking", page_icon="📧")
    
    st.title("📧 Email Spam Detection & IP Blocking")
    st.write("""
    Welcome to the Email Spam Detection & IP Blocking app. This tool helps you to:
    - Verify email addresses
    - Detect if an email is spam
    - Find and block the IP address of the email's domain
    """)
    
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Spam Detection", "Email Verification & IP Blocking", "Send Email"])
    
    if page == "Spam Detection":
        st.subheader("Spam Detection")
        
        email = st.text_area("Enter the email content:")
        if st.button("Check for Spam"):
            if email.strip():
                prediction = predict_spam(email)
                if prediction == 1:
                    st.warning("⚠️ Warning: This email is likely spam.")
                else:
                    st.success("✅ This email is not spam.")
            else:
                st.error("Please enter the email content.")
    
    elif page == "Email Verification & IP Blocking":
        st.subheader("Email Verification & IP Blocking")
        email = st.text_input("Enter an email address to verify:")
        if st.button("Verify Email"):
            if verify_email(email):
                st.success("✅ Valid Email Address")
                domain = email.split('@')[1]
                ip_address = find_ip_address(domain)
                if ip_address:
                    st.info(f"🌐 IP Address: {ip_address}")
                    if st.button("Block IP Address"):
                        block_ip(ip_address)
                        st.success("🛑 IP Address Blocked Successfully")
                else:
                    st.error("Failed to find IP address")
            else:
                st.error("❌ Invalid Email Address")
    
    elif page == "Send Email":
        st.subheader("Send Email")
        sender_email = st.text_input("Sender Email Address:")
        receiver_email = st.text_input("Receiver Email Address:", 'nehalkapgate@gmail.com')
        message = st.text_area("Email Message", """\
Subject: Sanika, I’m still waiting for your response

This message is sent from Saurabh Surashe.""")
        password = st.text_input("Email Password:", type='password')
        if st.button("Send Email"):
            if sender_email and receiver_email and message and password:
                send_mail(sender_email, receiver_email, password, message)
            else:
                st.error("Please fill in all fields.")

if __name__ == "__main__":
    main()
