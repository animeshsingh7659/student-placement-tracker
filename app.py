import datetime
import streamlit as st
from database import (
    init_db,
    add_application,
    update_application,
    delete_application,
    fetch_all_applications,
    get_application_by_id
)

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

STATUS_OPTIONS = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]

tab_add, tab_edit, tab_delete = st.tabs([
    "➕ Add Application",
    "✏️ Edit Application",
    "🗑️ Delete Application"
])

# ------------------ 1. ADD APPLICATION TAB ------------------
with tab_add:
    st.subheader("Add New Application")

    company = st.text_input("Company Name", placeholder="e.g. Google, Microsoft, Infosys", key="add_company")
    role = st.text_input("Job Role", placeholder="e.g. Software Engineer, Data Analyst", key="add_role")

    status = st.selectbox(
        "Application Status",
        STATUS_OPTIONS,
        key="add_status"
    )

    application_date = st.date_input("Application Date", key="add_date")
    ctc = st.number_input(
        "Package / CTC (LPA)",
        min_value=0.0,
        step=0.5,
        key="add_ctc"
    )

    if st.button("Add Application", type="primary", key="btn_add"):
        if not company.strip():
            st.error("Please enter a Company Name.")
        elif not role.strip():
            st.error("Please enter a Job Role.")
        else:
            add_application(company, role, status, application_date, ctc)
            st.success(f"Application for **{company}** ({role}) added successfully!")
            st.rerun()

# ------------------ 2. EDIT APPLICATION TAB ------------------
with tab_edit:
    st.subheader("Edit Existing Application")

    df_for_edit = fetch_all_applications()
    if not df_for_edit.empty:
        # Create a dictionary mapping ID -> Friendly Label
        app_options = {
            row["ID"]: f"ID {row['ID']} - {row['Company']} ({row['Job Role']})"
            for _, row in df_for_edit.iterrows()
        }

        selected_app_id = st.selectbox(
            "Select Application to Edit",
            options=list(app_options.keys()),
            format_func=lambda x: app_options[x],
            key="edit_select"
        )

        selected_app = get_application_by_id(selected_app_id)

        if selected_app:
            # Parse saved date safely into a datetime.date object
            try:
                default_date = datetime.date.fromisoformat(str(selected_app["application_date"]))
            except Exception:
                default_date = datetime.date.today()

            status_index = (
                STATUS_OPTIONS.index(selected_app["status"])
                if selected_app["status"] in STATUS_OPTIONS
                else 0
            )

            edit_company = st.text_input("Company Name", value=selected_app["company"], key="edit_company")
            edit_role = st.text_input("Job Role", value=selected_app["role"], key="edit_role")
            edit_status = st.selectbox("Application Status", STATUS_OPTIONS, index=status_index, key="edit_status")
            edit_date = st.date_input("Application Date", value=default_date, key="edit_date")
            edit_ctc = st.number_input(
                "Package / CTC (LPA)",
                value=float(selected_app["ctc"]),
                min_value=0.0,
                step=0.5,
                key="edit_ctc"
            )

            if st.button("Update Application", type="primary", key="btn_update"):
                if not edit_company.strip():
                    st.error("Please enter a Company Name.")
                elif not edit_role.strip():
                    st.error("Please enter a Job Role.")
                else:
                    update_application(selected_app_id, edit_company, edit_role, edit_status, edit_date, edit_ctc)
                    st.success(f"Application ID **{selected_app_id}** updated successfully!")
                    st.rerun()
    else:
        st.info("No applications available to edit. Add an application first!")

# ------------------ 3. DELETE APPLICATION TAB ------------------
with tab_delete:
    st.subheader("Delete Application")

    df_for_delete = fetch_all_applications()
    if not df_for_delete.empty:
        delete_options = {
            row["ID"]: f"ID {row['ID']} - {row['Company']} ({row['Job Role']}) - Status: {row['Status']}"
            for _, row in df_for_delete.iterrows()
        }

        selected_delete_id = st.selectbox(
            "Select Application to Delete",
            options=list(delete_options.keys()),
            format_func=lambda x: delete_options[x],
            key="delete_select"
        )

        st.warning(f"Are you sure you want to delete **{delete_options[selected_delete_id]}**? This action cannot be undone.")

        if st.button("Delete Application", type="primary", key="btn_delete"):
            delete_application(selected_delete_id)
            st.success(f"Application ID **{selected_delete_id}** deleted successfully!")
            st.rerun()
    else:
        st.info("No applications available to delete.")

# ------------------ 4. APPLICATION HISTORY ------------------
st.divider()

st.subheader("📋 Application History")
df_applications = fetch_all_applications()

if not df_applications.empty:
    st.dataframe(df_applications, use_container_width=True, hide_index=True)
else:
    st.info("No applications added yet. Start by filling out the form above!")