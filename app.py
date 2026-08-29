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

# ------------------ 1. GLOBAL CONSTANTS & PAGE SETUP ------------------
STATUS_OPTIONS = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]

st.set_page_config(
    page_title="Student Placement Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database on application startup
try:
    init_db()
except Exception as e:
    st.error(f"❌ Failed to initialize the database: {e}")

# ------------------ 2. SIDEBAR INFORMATION ------------------
with st.sidebar:
    st.title("🎓 Placement Tracker")
    st.caption("College Placement Cell Management Portal")
    st.divider()

    st.markdown("### 📌 Quick Guide")
    st.markdown(
        """
        - **Dashboard**: Live summary of your applications.
        - **Manage**: Add, edit, or remove placement applications.
        - **History**: Search, filter, and review records.
        - **Analytics**: Visual breakdowns of status, companies, and packages.
        """
    )
    st.divider()

    st.markdown("### ⚙️ System Status")
    st.success("Database: Connected (SQLite)")
    st.caption("All data is stored locally in `placement_tracker.db`.")

# ------------------ 3. MAIN HEADER ------------------
st.title("🎓 Student Placement Tracker")
st.markdown("Monitor and analyze your campus placement applications, interviews, and job offers in one centralized dashboard.")
st.markdown("<br>", unsafe_allow_html=True)

# ------------------ 4. OVERVIEW DASHBOARD METRICS ------------------
st.subheader("📊 Performance Overview")

try:
    metrics = get_application_metrics()
except Exception as e:
    st.warning(f"⚠️ Could not load metrics: {e}")
    metrics = {"total": 0, "applied": 0, "shortlisted": 0, "interview": 0, "selected": 0, "rejected": 0}

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = st.columns(6)

with metric_col1:
    with st.container(border=True):
        st.metric("Total Applications", metrics["total"], help="Total campus placements applied")

with metric_col2:
    with st.container(border=True):
        st.metric("Applied", metrics["applied"], help="Applications submitted and pending review")

with metric_col3:
    with st.container(border=True):
        st.metric("Shortlisted", metrics["shortlisted"], help="Shortlisted for tests/interviews")

with metric_col4:
    with st.container(border=True):
        st.metric("Interview", metrics["interview"], help="Currently in interview rounds")

with metric_col5:
    with st.container(border=True):
        st.metric("Selected", metrics["selected"], help="Job offers received")

with metric_col6:
    with st.container(border=True):
        st.metric("Rejected", metrics["rejected"], help="Applications not selected")

st.divider()

# Load all application records once for use across management tabs, history table, and analytics
try:
    df_applications = fetch_all_applications()
except Exception as e:
    st.error(f"❌ Failed to fetch application records from database: {e}")
    df_applications = None

# ------------------ 5. APPLICATION MANAGEMENT (ADD / EDIT / DELETE) ------------------
st.subheader("🛠️ Manage Applications")

tab_add, tab_edit, tab_delete = st.tabs([
    "➕ Add New Application",
    "✏️ Edit Application",
    "🗑️ Delete Application"
])

# --- TAB 1: ADD APPLICATION ---
with tab_add:
    with st.container(border=True):
        st.markdown("#### Enter Application Details")
        st.caption("Fill out the company and job information below to track a new application.")

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            company = st.text_input("🏢 Company Name", placeholder="e.g. Google, Microsoft, Infosys", key="add_company")
        with row1_col2:
            role = st.text_input("💼 Job Role", placeholder="e.g. Software Engineer, Data Analyst", key="add_role")

        row2_col1, row2_col2, row2_col3 = st.columns(3)
        with row2_col1:
            status = st.selectbox("📌 Application Status", STATUS_OPTIONS, key="add_status")
        with row2_col2:
            application_date = st.date_input("📅 Application Date", key="add_date")
        with row2_col3:
            ctc = st.number_input(
                "💰 Package / CTC (LPA)",
                value=0.0,
                step=0.5,
                key="add_ctc",
                help="Annual CTC offered in Lakhs Per Annum"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Application", type="primary", key="btn_add", use_container_width=True):
            if not company.strip():
                st.error("❌ Company Name cannot be empty or contain only whitespace.")
            elif not role.strip():
                st.error("❌ Job Role cannot be empty or contain only whitespace.")
            elif ctc < 0.0:
                st.error("❌ CTC cannot be negative.")
            elif not application_date:
                st.error("❌ Please select a valid application date.")
            else:
                try:
                    add_application(company, role, status, application_date, ctc)
                    st.success(f"✅ Application for **{company.strip()}** ({role.strip()}) added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to save application: {e}")

# --- TAB 2: EDIT APPLICATION ---
with tab_edit:
    with st.container(border=True):
        st.markdown("#### Update Existing Application")
        st.caption("Select an application from the dropdown below to modify its details.")

        if df_applications is not None and not df_applications.empty:
            app_options = {
                row["ID"]: f"ID {row['ID']} — {row['Company']} ({row['Job Role']}) [{row['Status']}]"
                for _, row in df_applications.iterrows()
            }

            selected_app_id = st.selectbox(
                "🎯 Select Application to Edit",
                options=list(app_options.keys()),
                format_func=lambda x: app_options[x],
                key="edit_select"
            )

            # Always fetch the fresh record for the selected application ID
            try:
                selected_app = get_application_by_id(selected_app_id)
            except Exception as e:
                st.error(f"❌ Error fetching application details: {e}")
                selected_app = None

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

                st.divider()
                edit_col1, edit_col2 = st.columns(2)
                # Dynamic keys tied to selected_app_id guarantee fresh state whenever selection changes
                with edit_col1:
                    edit_company = st.text_input(
                        "🏢 Company Name",
                        value=selected_app["company"],
                        key=f"edit_company_{selected_app_id}"
                    )
                with edit_col2:
                    edit_role = st.text_input(
                        "💼 Job Role",
                        value=selected_app["role"],
                        key=f"edit_role_{selected_app_id}"
                    )

                edit_row2_col1, edit_row2_col2, edit_row2_col3 = st.columns(3)
                with edit_row2_col1:
                    edit_status = st.selectbox(
                        "📌 Application Status",
                        STATUS_OPTIONS,
                        index=status_index,
                        key=f"edit_status_{selected_app_id}"
                    )
                with edit_row2_col2:
                    edit_date = st.date_input(
                        "📅 Application Date",
                        value=default_date,
                        key=f"edit_date_{selected_app_id}"
                    )
                with edit_row2_col3:
                    edit_ctc = st.number_input(
                        "💰 Package / CTC (LPA)",
                        value=float(selected_app["ctc"]),
                        step=0.5,
                        key=f"edit_ctc_{selected_app_id}"
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Save Changes", type="primary", key=f"btn_update_{selected_app_id}", use_container_width=True):
                    if not edit_company.strip():
                        st.error("❌ Company Name cannot be empty or contain only whitespace.")
                    elif not edit_role.strip():
                        st.error("❌ Job Role cannot be empty or contain only whitespace.")
                    elif edit_ctc < 0.0:
                        st.error("❌ CTC cannot be negative.")
                    elif not edit_date:
                        st.error("❌ Please select a valid application date.")
                    else:
                        try:
                            update_application(selected_app_id, edit_company, edit_role, edit_status, edit_date, edit_ctc)
                            st.success(f"✅ Application ID **{selected_app_id}** updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to update application: {e}")
        else:
            st.info("No applications available to edit. Add an application first!")

# --- TAB 3: DELETE APPLICATION ---
with tab_delete:
    with st.container(border=True):
        st.markdown("#### Remove an Application")
        st.caption("Select an application you wish to permanently delete from the database.")

        if df_applications is not None and not df_applications.empty:
            delete_options = {
                row["ID"]: f"ID {row['ID']} — {row['Company']} ({row['Job Role']}) [{row['Status']}] — {row['CTC (LPA)']} LPA"
                for _, row in df_applications.iterrows()
            }

            selected_delete_id = st.selectbox(
                "🎯 Select Application to Delete",
                options=list(delete_options.keys()),
                format_func=lambda x: delete_options[x],
                key="delete_select"
            )

            st.warning(f"⚠️ **Confirm Deletion**: Are you sure you want to delete **{delete_options[selected_delete_id]}**? This action cannot be undone.")

            if st.button("🗑️ Permanently Delete Application", type="primary", key=f"btn_delete_{selected_delete_id}", use_container_width=True):
                try:
                    delete_application(selected_delete_id)
                    st.success(f"✅ Application ID **{selected_delete_id}** deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to delete application: {e}")
        else:
            st.info("No applications available to delete.")

st.divider()

# ------------------ 6. APPLICATION HISTORY (SEARCH & FILTER) ------------------
st.subheader("📋 Application Records")

if df_applications is not None and not df_applications.empty:
    with st.container(border=True):
        search_col, filter_col = st.columns([3, 1])

        with search_col:
            search_query = st.text_input(
                "🔍 Search Records",
                placeholder="Type company name or job role...",
                key="search_query"
            )

        with filter_col:
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
            st.dataframe(
                df_filtered,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Company": st.column_config.TextColumn("🏢 Company", width="medium"),
                    "Job Role": st.column_config.TextColumn("💼 Job Role", width="medium"),
                    "Status": st.column_config.TextColumn("📌 Status", width="small"),
                    "Date Applied": st.column_config.DateColumn("📅 Date Applied", format="YYYY-MM-DD"),
                    "CTC (LPA)": st.column_config.NumberColumn("💰 CTC (LPA)", format="%.1f LPA"),
                    "Created At": st.column_config.DatetimeColumn("🕒 Logged At", format="YYYY-MM-DD HH:mm")
                }
            )
            st.caption(f"Showing **{len(df_filtered)}** of **{len(df_applications)}** total recorded applications")
        else:
            st.warning("No applications found matching your search and filter criteria.")
else:
    st.info("No applications added yet. Start by adding your first application above!")

st.divider()

# ------------------ 7. PLACEMENT ANALYTICS ------------------
st.subheader("📊 Placement Analytics & Insights")

if df_applications is not None and not df_applications.empty:
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Applications by Status
    with chart_col1:
        with st.container(border=True):
            status_df = df_applications["Status"].value_counts().reset_index()
            status_df.columns = ["Status", "Count"]

            fig_status = px.bar(
                status_df,
                x="Status",
                y="Count",
                text="Count",
                title="<b>Applications by Status</b>",
                labels={"Status": "Status", "Count": "Count"},
                color="Status",
                template="plotly_white"
            )
            fig_status.update_traces(textposition="outside")
            fig_status.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="Application Status",
                yaxis_title="Number of Applications"
            )
            st.plotly_chart(fig_status, use_container_width=True)

    # Chart 2: Applications by Company
    with chart_col2:
        with st.container(border=True):
            company_df = df_applications["Company"].value_counts().reset_index()
            company_df.columns = ["Company", "Count"]

            fig_company = px.bar(
                company_df,
                x="Company",
                y="Count",
                text="Count",
                title="<b>Applications per Company</b>",
                labels={"Company": "Company", "Count": "Count"},
                color="Company",
                template="plotly_white"
            )
            fig_company.update_traces(textposition="outside")
            fig_company.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="Company Name",
                yaxis_title="Number of Applications"
            )
            st.plotly_chart(fig_company, use_container_width=True)

    # Chart 3: CTC / Package Analysis by Company (in LPA)
    with st.container(border=True):
        fig_ctc = px.bar(
            df_applications,
            x="Company",
            y="CTC (LPA)",
            color="Status",
            text="CTC (LPA)",
            hover_data=["Job Role", "Date Applied"],
            title="<b>Package / CTC Analysis by Company (in LPA)</b>",
            labels={"Company": "Company Name", "CTC (LPA)": "Package (LPA)", "Status": "Status"},
            template="plotly_white"
        )
        fig_ctc.update_traces(texttemplate="%{text} LPA", textposition="outside")
        fig_ctc.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Company Name",
            yaxis_title="CTC (LPA)"
        )
        st.plotly_chart(fig_ctc, use_container_width=True)

else:
    st.info("Add applications above to generate interactive analytics visualizations!")