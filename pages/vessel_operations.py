# pages/vessel_operations.py
import streamlit as st
import pandas as pd
from io import BytesIO


def show_vessel_page(db):
    """Vessel management page with tabs"""

    tab = st.radio("", ["➕ Add Vessel", "📊 View & Search", "📤 Bulk Upload"],
                   horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if tab == "➕ Add Vessel":
        show_add_vessel(db)
    elif tab == "📊 View & Search":
        show_view_vessels(db)
    elif tab == "📤 Bulk Upload":
        show_bulk_upload_vessels(db)


def show_add_vessel(db):
    """Add vessel manually"""
    st.subheader("Enter Vessel Details Manually")

    vessel_name = st.text_input("Vessel Name *", placeholder="Enter vessel name")

    master_manager_email = st.text_area(
        "Master/Manager Email ID *",
        placeholder="Enter email addresses (one per line or comma-separated)\nExample:\nmaster@ship.com\nmanager@company.com",
        height=120
    )

    contact_details = st.text_area(
        "Contact Details",
        placeholder="Enter contact information:\n\nPhone Numbers:\n+971 123 456 789\n\nOffice Address:\nPort Office Building\nFloor 5, Suite 501\nDubai, UAE",
        height=200
    )

    if st.button("Submit", use_container_width=True, type="primary"):
        if vessel_name and master_manager_email:
            success, message = db.insert_vessel(
                vessel_name.strip(),
                master_manager_email.strip(),
                contact_details.strip() if contact_details else ""
            )
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)
        else:
            st.warning("Please fill in all required fields!")


@st.dialog("⚠️ Confirm Deletion")
def confirm_bulk_delete_vessel_dialog(selected_count):
    """Popup dialog for bulk delete confirmation"""
    st.warning(f"You are about to delete **{selected_count}** vessel(s).")
    st.error("⚠️ This action cannot be undone!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Delete All", type="primary", use_container_width=True, key="confirm_delete_vessel_popup"):
            st.session_state.confirm_bulk_delete_vessel_confirmed = True
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key="cancel_delete_vessel_popup"):
            st.session_state.confirm_bulk_delete_vessel = False
            st.rerun()


@st.dialog("⚠️ Confirm Deletion")
def confirm_single_delete_vessel_dialog(vessel_name, vessel_id):
    """Popup dialog for single delete confirmation"""
    st.warning(f"Delete **{vessel_name}**?")
    st.error("⚠️ This action cannot be undone!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Delete", type="primary", use_container_width=True,
                     key=f"confirm_single_vessel_popup_{vessel_id}"):
            st.session_state.confirm_single_delete_vessel_confirmed = vessel_id
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key=f"cancel_single_vessel_popup_{vessel_id}"):
            st.session_state[f"confirm_delete_vessel_{vessel_id}"] = False
            st.rerun()


def show_view_vessels(db):
    """View all vessels with bulk delete"""

    # Initialize session state
    if 'selected_vessels' not in st.session_state:
        st.session_state.selected_vessels = []
    if 'bulk_delete_vessel_mode' not in st.session_state:
        st.session_state.bulk_delete_vessel_mode = False

    # Handle bulk delete confirmation
    if st.session_state.get('confirm_bulk_delete_vessel_confirmed', False):
        deleted_count = 0
        for vessel_id in st.session_state.selected_vessels:
            success, message = db.delete_vessel(vessel_id)
            if success:
                deleted_count += 1

        st.session_state.selected_vessels = []
        st.session_state.confirm_bulk_delete_vessel = False
        st.session_state.bulk_delete_vessel_mode = False
        st.session_state.confirm_bulk_delete_vessel_confirmed = False

        st.success(f"✅ Successfully deleted {deleted_count} vessel(s)!")
        st.balloons()
        st.rerun()

    # Handle single delete confirmation
    if st.session_state.get('confirm_single_delete_vessel_confirmed', False):
        vessel_id = st.session_state.confirm_single_delete_vessel_confirmed
        success, message = db.delete_vessel(vessel_id)
        if success:
            st.success(message)
            if f"confirm_delete_vessel_{vessel_id}" in st.session_state:
                del st.session_state[f"confirm_delete_vessel_{vessel_id}"]
            st.session_state.confirm_single_delete_vessel_confirmed = False
            st.balloons()
            st.rerun()
        else:
            st.error(message)
            st.session_state.confirm_single_delete_vessel_confirmed = False

    # Search bar and bulk delete toggle
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search by Vessel Name, Email, or Contact", placeholder="Type to search...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear Search", use_container_width=True, key="clear_search_vessel"):
            search_term = ""
            st.rerun()
    with col3:
        st.write("")
        st.write("")
        if st.session_state.bulk_delete_vessel_mode:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_bulk_vessel_mode"):
                st.session_state.bulk_delete_vessel_mode = False
                st.session_state.selected_vessels = []
                st.rerun()
        else:
            if st.button("🗑️ Bulk Delete", use_container_width=True, key="enable_bulk_vessel_mode", type="primary"):
                st.session_state.bulk_delete_vessel_mode = True
                st.rerun()

    # Get vessels based on search
    if search_term:
        vessels = db.search_vessel(search_term)
        st.info(f"Found {len(vessels)} vessel(s) matching '{search_term}'")
    else:
        vessels = db.get_all_vessels()
        if vessels:
            st.info(f"Total vessels: {len(vessels)}")

    if vessels:
        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Vessels", len(vessels))
        with col2:
            email_count = sum(1 for v in vessels if v.get('master_manager_email'))
            st.metric("With Emails", email_count)

        st.markdown("---")

        # Show bulk delete controls when in bulk delete mode
        if st.session_state.bulk_delete_vessel_mode:
            st.warning("🗑️ **Bulk Delete Mode** - Select vessels and click 'Delete Selected'")

            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

            with col1:
                select_all = st.checkbox("Select All", key="select_all_vessel")
                if select_all:
                    st.session_state.selected_vessels = [v['id'] for v in vessels]
                elif not select_all and len(st.session_state.selected_vessels) == len(vessels):
                    st.session_state.selected_vessels = []

            with col2:
                if st.button("Clear Selection", key="clear_vessel_sel"):
                    st.session_state.selected_vessels = []
                    st.rerun()

            with col3:
                st.info(f"Selected: {len(st.session_state.selected_vessels)}")

            with col4:
                if st.session_state.selected_vessels:
                    if st.button(f"Delete {len(st.session_state.selected_vessels)} Selected",
                                 type="primary", key="delete_selected_vessel_btn"):
                        st.session_state.confirm_bulk_delete_vessel = True
                        st.rerun()

            # Show popup dialog for bulk delete
            if st.session_state.get('confirm_bulk_delete_vessel', False):
                confirm_bulk_delete_vessel_dialog(len(st.session_state.selected_vessels))

            st.markdown("---")

        # Display vessels
        for idx, vessel in enumerate(vessels):

            # Only show checkboxes in bulk delete mode
            if st.session_state.bulk_delete_vessel_mode:
                col_check, col_expand = st.columns([0.5, 9.5])

                with col_check:
                    is_selected = vessel['id'] in st.session_state.selected_vessels
                    if st.checkbox("", value=is_selected, key=f"check_vessel_{vessel['id']}",
                                   label_visibility="collapsed"):
                        if vessel['id'] not in st.session_state.selected_vessels:
                            st.session_state.selected_vessels.append(vessel['id'])
                    else:
                        if vessel['id'] in st.session_state.selected_vessels:
                            st.session_state.selected_vessels.remove(vessel['id'])

                with col_expand:
                    with st.expander(f"🚢 {vessel['vessel_name']}", expanded=False):
                        st.markdown(f"**VESSEL NAME:** {vessel['vessel_name']}")
                        st.text_area("Master/Manager Email", vessel.get('master_manager_email', ''),
                                     height=100, disabled=True, key=f"email_bulk_{vessel['id']}")
                        if vessel.get('contact_details'):
                            st.text_area("Contact Details", vessel['contact_details'],
                                         height=150, disabled=True, key=f"contact_bulk_{vessel['id']}")
                        st.caption(f"Created: {vessel.get('created_at', 'N/A')}")

            else:
                # Normal mode - no checkboxes
                with st.expander(f"🚢 {vessel['vessel_name']}", expanded=False):
                    if f"edit_mode_vessel_{vessel['id']}" not in st.session_state:
                        st.session_state[f"edit_mode_vessel_{vessel['id']}"] = False

                    if not st.session_state[f"edit_mode_vessel_{vessel['id']}"]:
                        # DISPLAY MODE
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**VESSEL NAME:** {vessel['vessel_name']}")
                            st.text_area("Master/Manager Email", vessel.get('master_manager_email', ''),
                                         height=100, disabled=True, key=f"email_display_{vessel['id']}")
                            if vessel.get('contact_details'):
                                st.text_area("Contact Details", vessel['contact_details'],
                                             height=150, disabled=True, key=f"contact_display_{vessel['id']}")
                            st.caption(f"Created: {vessel.get('created_at', 'N/A')}")

                        with col2:
                            st.write("")
                            st.write("")
                            if st.button("✏️ Edit", key=f"edit_vessel_btn_{vessel['id']}", use_container_width=True):
                                st.session_state[f"edit_mode_vessel_{vessel['id']}"] = True
                                st.rerun()

                            if st.button("🗑️ Delete", key=f"delete_vessel_btn_{vessel['id']}",
                                         use_container_width=True, type="secondary"):
                                st.session_state[f"confirm_delete_vessel_{vessel['id']}"] = True
                                st.rerun()

                        # Show popup dialog for single delete
                        if st.session_state.get(f"confirm_delete_vessel_{vessel['id']}", False):
                            confirm_single_delete_vessel_dialog(vessel['vessel_name'], vessel['id'])

                    else:
                        # EDIT MODE
                        st.subheader("✏️ Edit Vessel Details")

                        edit_vessel_name = st.text_input("VESSEL NAME *", value=vessel['vessel_name'],
                                                         key=f"edit_vessel_name_{vessel['id']}")
                        edit_email = st.text_area("MASTER/MANAGER EMAIL *",
                                                  value=vessel.get('master_manager_email', ''),
                                                  height=100, key=f"edit_vessel_email_{vessel['id']}")
                        edit_contact = st.text_area("CONTACT DETAILS",
                                                    value=vessel.get('contact_details', ''),
                                                    height=200, key=f"edit_vessel_contact_{vessel['id']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Save", key=f"save_vessel_btn_{vessel['id']}",
                                         use_container_width=True, type="primary"):
                                if edit_vessel_name and edit_email:
                                    success, message = db.update_vessel(
                                        vessel['id'],
                                        edit_vessel_name.strip(),
                                        edit_email.strip(),
                                        edit_contact.strip() if edit_contact else ""
                                    )
                                    if success:
                                        st.success(message)
                                        st.session_state[f"edit_mode_vessel_{vessel['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                                else:
                                    st.warning("Vessel name and email required!")

                        with col2:
                            if st.button("❌ Cancel", key=f"cancel_vessel_btn_{vessel['id']}", use_container_width=True):
                                st.session_state[f"edit_mode_vessel_{vessel['id']}"] = False
                                st.rerun()

        # Export
        st.markdown("---")
        df = pd.DataFrame(vessels)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vessels')
        output.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name=f"vessel_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("No vessels found. Add vessels using the tabs above.")


def show_bulk_upload_vessels(db):
    """Bulk upload vessels from Excel"""
    st.subheader("Upload Vessel Details from Excel")

    st.info("""
    📋 **Excel File Format Requirements:**

    **Option 1: Column Position (Easiest)**
    - 1st Column = Vessel Name
    - 2nd Column = Master/Manager Email
    - 3rd Column = Contact Details

    **Option 2: Named Columns (Flexible)**
    - Any variation of: vessel name, email, contact

    ✅ Case-insensitive, flexible format
    """)

    # Download template
    st.markdown("### 📥 Download Template")
    template_df = pd.DataFrame({
        'vessel_name': ['Example Ship 1', 'Example Ship 2'],
        'master_manager_email': [
            'master1@example.com, manager1@example.com',
            'master2@example.com, manager2@example.com'
        ],
        'contact_details': [
            'Phone: +971123456789\nOffice: Dubai Port',
            'Phone: +971987654321\nOffice: Abu Dhabi Port'
        ]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name='Vessels')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Template",
        data=output,
        file_name="vessel_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'], key="vessel_upload")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # Column mapping
            column_mapping = {
                'vessel': 'vessel_name',
                'vessel_name': 'vessel_name',
                'ship_name': 'vessel_name',
                'ship': 'vessel_name',
                'name': 'vessel_name',
                'email': 'master_manager_email',
                'emails': 'master_manager_email',
                'master_manager_email': 'master_manager_email',
                'master_email': 'master_manager_email',
                'contact': 'contact_details',
                'contact_details': 'contact_details',
            }

            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)

            required_columns = ['vessel_name', 'master_manager_email']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.warning("""
                **Please ensure your Excel file has:**
                - Vessel Name (column 1 or named: vessel_name, vessel, ship_name, ship, name)
                - Email (column 2 or named: master_manager_email, email, emails, master_email)
                - Contact Details (optional: column 3 or named: contact_details, contact)
                """)
            else:
                if 'contact_details' not in df.columns:
                    df['contact_details'] = ''

                df = df[['vessel_name', 'master_manager_email', 'contact_details']]

                # Clean data
                for col in df.columns:
                    df[col] = df[col].fillna('')

                # Count valid records
                valid_records = df[(df['vessel_name'] != '') & (df['master_manager_email'] != '')]
                valid_count = len(valid_records)
                invalid_count = len(df) - valid_count

                # Show detection message
                st.success(f"✅ File uploaded! Detected {len(df)} records")

                # Show summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📋 Total Records", len(df))
                with col2:
                    st.metric("✅ Valid Records", valid_count)
                with col3:
                    st.metric("⚠️ Invalid Records", invalid_count)

                if invalid_count > 0:
                    st.warning(f"⚠️ {invalid_count} record(s) have missing required fields and will be skipped")

                st.markdown("---")

                if valid_count > 0:
                    if st.button(f"📤 Import {valid_count} Valid Records", type="primary", use_container_width=True):
                        with st.spinner(f"Importing {valid_count} record(s)..."):
                            vessels_data = valid_records.to_dict('records')

                            success_count, failed_records = db.insert_vessels_bulk(vessels_data)

                            st.markdown("---")

                            if success_count > 0:
                                st.success(f"✅ Successfully imported {success_count} vessel(s)!")

                                # Show imported records
                                st.markdown("### 📋 Imported Vessels:")
                                for idx, row in valid_records.head(success_count).iterrows():
                                    with st.expander(f"✅ {row['vessel_name']}", expanded=False):
                                        st.write(f"**Email:** {row['master_manager_email']}")
                                        if row.get('contact_details'):
                                            st.text_area("Contact Details", row['contact_details'],
                                                         height=100, disabled=True, key=f"vessel_imported_{idx}")

                            if failed_records:
                                st.error(f"❌ Failed to import {len(failed_records)} record(s)")

                                with st.expander("❌ Failed Records (Click to view)", expanded=False):
                                    for fail in failed_records:
                                        st.write(
                                            f"**Row {fail.get('row', 'N/A')}:** {fail.get('reason', 'Unknown error')}")
                                        if fail.get('vessel_name'):
                                            st.write(f"   - Vessel: {fail['vessel_name']}")
                                        st.markdown("---")

                            if success_count == len(vessels_data):
                                st.balloons()
                else:
                    st.error("❌ No valid records to import!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")