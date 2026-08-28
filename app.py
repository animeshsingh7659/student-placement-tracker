import datetime
import streamlit as st
import plotly.express as px
from database import (
    init_db,
    add_application,
    update_application,
    delete_application,
    fetch_all_applications,
    get_application_by_id,
    get_application_metrics
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

# ------------------ 1. OVERVIEW DASHBOARD METRICS ------------------
metrics = get_application_metrics()

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Applications", metrics["total"])
with col2:
    st.metric("Applied", metrics["applied"])
with col3:
    st.metric("Shortlisted", metrics["shortlisted"])
with col4:
    st.metric("Interview", metrics["interview"])
with col5:
    st.metric("Selected", metrics["selected"])
with col6:
    st.metric("Rejected", metrics["rejected"])

st.divider()

STATUS_OPTIONS = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]

# ------------------ 2. ACTION TABS (ADD / EDIT / DELETE) ------------------
tab_add, tab_edit, tab_delete = st.tabs([
    "➕ Add Application",
    "✏️ Edit Application",
    "🗑️ Delete Application"
])

# --- ADD APPLICATION TAB ---
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

# --- EDIT APPLICATION TAB ---
with tab_edit:
    st.subheader("Edit Existing Application")

    df_for_edit = fetch_all_applications()
    if not df_for_edit.empty:
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

# --- DELETE APPLICATION TAB ---
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

# ------------------ 3. APPLICATION HISTORY (WITH SEARCH & FILTER) ------------------
st.divider()

st.subheader("📋 Application History")
df_applications = fetch_all_applications()

if not df_applications.empty:
    col_search, col_filter = st.columns([2, 1])

    with col_search:
        search_query = st.text_input(
            "🔍 Search Applications",
            placeholder="Search by company name or job role...",
            key="search_query"
        )

    with col_filter:
        status_filter = st.selectbox(
            "📌 Filter by Status",
            options=["All Statuses"] + STATUS_OPTIONS,
            key="status_filter"
        )

    df_filtered = df_applications.copy()

    if status_filter != "All Statuses":
        df_filtered = df_filtered[df_filtered["Status"] == status_filter]

    if search_query.strip():
        query = search_query.strip().lower()
        df_filtered = df_filtered[
            df_filtered["Company"].str.lower().str.contains(query, na=False) |
            df_filtered["Job Role"].str.lower().str.contains(query, na=False)
        ]

    if not df_filtered.empty:
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        st.caption(f"Showing **{len(df_filtered)}** of **{len(df_applications)}** total applications")
    else:
        st.warning("No applications found matching your search and filter criteria.")
else:
    st.info("No applications added yet. Start by filling out the form above!")

# ------------------ 4. PLACEMENT ANALYTICS ------------------
st.divider()

st.subheader("📊 Placement Analytics")

if not df_applications.empty:
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Applications by Status
    with chart_col1:
        status_df = df_applications["Status"].value_counts().reset_index()
        status_df.columns = ["Status", "Count"]

        fig_status = px.bar(
            status_df,
            x="Status",
            y="Count",
            text="Count",
            title="Applications by Status",
            labels={"Status": "Application Status", "Count": "Number of Applications"},
            color="Status"
        )
        fig_status.update_traces(textposition="outside")
        fig_status.update_layout(showlegend=False, xaxis_title="Status", yaxis_title="Count")
        st.plotly_chart(fig_status, use_container_width=True)

    # Chart 2: Applications by Company
    with chart_col2:
        company_df = df_applications["Company"].value_counts().reset_index()
        company_df.columns = ["Company", "Count"]

        fig_company = px.bar(
            company_df,
            x="Company",
            y="Count",
            text="Count",
            title="Applications by Company",
            labels={"Company": "Company Name", "Count": "Number of Applications"},
            color="Company"
        )
        fig_company.update_traces(textposition="outside")
        fig_company.update_layout(showlegend=False, xaxis_title="Company", yaxis_title="Count")
        st.plotly_chart(fig_company, use_container_width=True)

    # Chart 3: CTC / Package Analysis by Company (in LPA)
    fig_ctc = px.bar(
        df_applications,
        x="Company",
        y="CTC (LPA)",
        color="Status",
        text="CTC (LPA)",
        hover_data=["Job Role", "Date Applied"],
        title="Package / CTC Analysis by Company (in LPA)",
        labels={"Company": "Company Name", "CTC (LPA)": "Package (LPA)", "Status": "Status"}
    )
    fig_ctc.update_traces(texttemplate="%{text} LPA", textposition="outside")
    fig_ctc.update_layout(xaxis_title="Company", yaxis_title="CTC (LPA)")
    st.plotly_chart(fig_ctc, use_container_width=True)

else:
    st.info("Add applications above to see interactive visual analytics!")