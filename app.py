import streamlit as st

st.set_page_config(
    page_title="Student Placement Tracker",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Placement Tracker")
st.write("Track your placement applications in one place.")

st.divider()

st.subheader("Add New Application")

company = st.text_input("Company Name")
role = st.text_input("Job Role")

status = st.selectbox(
    "Application Status",
    ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]
)

application_date = st.date_input("Application Date")
ctc = st.number_input(
    "Package / CTC (LPA)",
    min_value=0.0,
    step=0.5
)

if st.button("Add Application"):
    st.success("Application added successfully!")