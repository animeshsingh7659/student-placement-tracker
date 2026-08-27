import streamlit as st
from database import init_db, add_application, fetch_all_applications

# Configure page settings (must be the first Streamlit command)
st.set_page_config(
    page_title="Student Placement Tracker",
    page_icon="🎓",
    layout="wide"
)

# Initialize the database on app load
init_db()

st.title("🎓 Student Placement Tracker")
st.write("Track your placement applications in one place.")

st.divider()

st.subheader("Add New Application")

company = st.text_input("Company Name", placeholder="e.g. Google, Microsoft, Infosys")
role = st.text_input("Job Role", placeholder="e.g. Software Engineer, Data Analyst")

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

if st.button("Add Application", type="primary"):
    if not company.strip():
        st.error("Please enter a Company Name.")
    elif not role.strip():
        st.error("Please enter a Job Role.")
    else:
        add_application(company, role, status, application_date, ctc)
        st.success(f"Application for **{company}** ({role}) added successfully!")
        st.rerun()

st.divider()

st.subheader("📋 Application History")
df_applications = fetch_all_applications()

if not df_applications.empty:
    st.dataframe(df_applications, use_container_width=True, hide_index=True)
else:
    st.info("No applications added yet. Start by filling out the form above!")