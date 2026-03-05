# pages/manager_operations.py
import streamlit as st
import pandas as pd
from io import BytesIO


def show_manager_page(db):
    """Manager management page with tabs"""

    tab = st.radio("", ["➕ Add Manager", "📊 View & Search", "📤 Bulk Upload"],
                   horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if tab == "➕ Add Manager":
        show_add_manager(db)
    elif tab == "📊 View & Search":
        show_view_managers(db)
    elif tab == "📤 Bulk Upload":
        show_bulk_upload_managers(db)


def show_add_manager(db):
    """Add manager manually"""
    st.subheader("Enter Manager Details Manually")

    company_name = st.text_input("COMPANY NAME *", placeholder="Enter company name")
    email_id = st.text_input("EMAIL ID *", placeholder="Enter email address")
    address_and_contact = st.text_area(
        "ADDRESS AND CONTACT *",
        placeholder="Enter complete address and contact details:\n\nOffice Address:\nBuilding Name, Floor\nStreet Name\nCity, Country\nP.O. Box: xxxxx\n\nContact: +971 12 345 6789",
        height=200
    )

    if st.button("Submit", use_container_width=True, type="primary"):
        if company_name and email_id and address_and_contact:
            success, message = db.insert_manager(
                company_name.strip(),
                email_id.strip(),
                address_and_contact.strip()
            )
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)
        else:
            st.warning("Please fill in all required fields!")


@st.dialog("⚠️ Confirm Deletion")
def confirm_bulk_delete_dialog(selected_count):
    """Popup dialog for bulk delete confirmation"""
    st.warning(f"You are about to delete **{selected_count}** manager(s).")
    st.error("⚠️ This action cannot be undone!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Delete All", type="primary", use_container_width=True, key="confirm_delete_popup"):
            st.session_state.confirm_bulk_delete_confirmed = True
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key="cancel_delete_popup"):
            st.session_state.confirm_bulk_delete_mgr = False
            st.rerun()


@st.dialog("⚠️ Confirm Deletion")
def confirm_single_delete_dialog(manager_name, manager_id):
    """Popup dialog for single delete confirmation"""
    st.warning(f"Delete **{manager_name}**?")
    st.error("⚠️ This action cannot be undone!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Delete", type="primary", use_container_width=True,
                     key=f"confirm_single_popup_{manager_id}"):
            st.session_state.confirm_single_delete_confirmed = manager_id
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key=f"cancel_single_popup_{manager_id}"):
            st.session_state[f"confirm_delete_{manager_id}"] = False
            st.rerun()


def show_view_managers(db):
    """View and search managers with bulk delete"""

    # Initialize session state
    if 'selected_managers' not in st.session_state:
        st.session_state.selected_managers = []
    if 'bulk_delete_mode' not in st.session_state:
        st.session_state.bulk_delete_mode = False

    # Handle bulk delete confirmation
    if st.session_state.get('confirm_bulk_delete_confirmed', False):
        deleted_count = 0
        for manager_id in st.session_state.selected_managers:
            success, message = db.delete_manager(manager_id)
            if success:
                deleted_count += 1

        st.session_state.selected_managers = []
        st.session_state.confirm_bulk_delete_mgr = False
        st.session_state.bulk_delete_mode = False
        st.session_state.confirm_bulk_delete_confirmed = False

        st.success(f"✅ Successfully deleted {deleted_count} manager(s)!")
        st.balloons()
        st.rerun()

    # Handle single delete confirmation
    if st.session_state.get('confirm_single_delete_confirmed', False):
        manager_id = st.session_state.confirm_single_delete_confirmed
        success, message = db.delete_manager(manager_id)
        if success:
            st.success(message)
            if f"confirm_delete_{manager_id}" in st.session_state:
                del st.session_state[f"confirm_delete_{manager_id}"]
            st.session_state.confirm_single_delete_confirmed = False
            st.balloons()
            st.rerun()
        else:
            st.error(message)
            st.session_state.confirm_single_delete_confirmed = False

    # Search bar and bulk delete toggle
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search by Company Name, Email, or Address", placeholder="Type to search...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear Search", use_container_width=True, key="clear_search_mgr"):
            search_term = ""
            st.rerun()
    with col3:
        st.write("")
        st.write("")
        if st.session_state.bulk_delete_mode:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_bulk_mode"):
                st.session_state.bulk_delete_mode = False
                st.session_state.selected_managers = []
                st.rerun()
        else:
            if st.button("🗑️ Bulk Delete", use_container_width=True, key="enable_bulk_mode", type="primary"):
                st.session_state.bulk_delete_mode = True
                st.rerun()

    # Get managers based on search
    if search_term:
        managers = db.search_manager(search_term)
        st.info(f"Found {len(managers)} manager(s) matching '{search_term}'")
    else:
        managers = db.get_all_managers()
        if managers:
            st.info(f"Total managers: {len(managers)}")

    if managers:
        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Managers", len(managers))
        with col2:
            unique_companies = len(set([m['company_name'] for m in managers]))
            st.metric("Unique Companies", unique_companies)

        st.markdown("---")

        # Show bulk delete controls when in bulk delete mode
        if st.session_state.bulk_delete_mode:
            st.warning("🗑️ **Bulk Delete Mode** - Select managers and click 'Delete Selected'")

            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

            with col1:
                select_all = st.checkbox("Select All", key="select_all_mgr")
                if select_all:
                    st.session_state.selected_managers = [m['id'] for m in managers]
                elif not select_all and len(st.session_state.selected_managers) == len(managers):
                    st.session_state.selected_managers = []

            with col2:
                if st.button("Clear Selection", key="clear_sel"):
                    st.session_state.selected_managers = []
                    st.rerun()

            with col3:
                st.info(f"Selected: {len(st.session_state.selected_managers)}")

            with col4:
                if st.session_state.selected_managers:
                    if st.button(f"Delete {len(st.session_state.selected_managers)} Selected",
                                 type="primary", key="delete_selected_btn"):
                        st.session_state.confirm_bulk_delete_mgr = True
                        st.rerun()

            # Show popup dialog for bulk delete
            if st.session_state.get('confirm_bulk_delete_mgr', False):
                confirm_bulk_delete_dialog(len(st.session_state.selected_managers))

            st.markdown("---")

        # Display managers
        for idx, manager in enumerate(managers):

            # Only show checkboxes in bulk delete mode
            if st.session_state.bulk_delete_mode:
                col_check, col_expand = st.columns([0.5, 9.5])

                with col_check:
                    is_selected = manager['id'] in st.session_state.selected_managers
                    if st.checkbox("", value=is_selected, key=f"check_{manager['id']}",
                                   label_visibility="collapsed"):
                        if manager['id'] not in st.session_state.selected_managers:
                            st.session_state.selected_managers.append(manager['id'])
                    else:
                        if manager['id'] in st.session_state.selected_managers:
                            st.session_state.selected_managers.remove(manager['id'])

                with col_expand:
                    with st.expander(f"🏢 {manager['company_name']}", expanded=False):
                        st.markdown(f"**COMPANY NAME:** {manager['company_name']}")
                        st.markdown(f"**EMAIL ID:** {manager['email_id']}")
                        st.text_area("ADDRESS AND CONTACT", manager.get('address_and_contact', ''),
                                     height=150, disabled=True, key=f"addr_bulk_{manager['id']}")
                        st.caption(f"Created: {manager.get('created_at', 'N/A')}")

            else:
                # Normal mode - no checkboxes
                with st.expander(f"🏢 {manager['company_name']}", expanded=False):
                    if f"edit_mode_{manager['id']}" not in st.session_state:
                        st.session_state[f"edit_mode_{manager['id']}"] = False

                    if not st.session_state[f"edit_mode_{manager['id']}"]:
                        # DISPLAY MODE
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**COMPANY NAME:** {manager['company_name']}")
                            st.markdown(f"**EMAIL ID:** {manager['email_id']}")
                            st.text_area("ADDRESS AND CONTACT", manager.get('address_and_contact', ''),
                                         height=150, disabled=True, key=f"addr_display_{manager['id']}")
                            st.caption(f"Created: {manager.get('created_at', 'N/A')}")

                        with col2:
                            st.write("")
                            st.write("")
                            if st.button("✏️ Edit", key=f"edit_btn_{manager['id']}", use_container_width=True):
                                st.session_state[f"edit_mode_{manager['id']}"] = True
                                st.rerun()

                            if st.button("🗑️ Delete", key=f"delete_btn_{manager['id']}",
                                         use_container_width=True, type="secondary"):
                                st.session_state[f"confirm_delete_{manager['id']}"] = True
                                st.rerun()

                        # Show popup dialog for single delete
                        if st.session_state.get(f"confirm_delete_{manager['id']}", False):
                            confirm_single_delete_dialog(manager['company_name'], manager['id'])

                    else:
                        # EDIT MODE
                        st.subheader("✏️ Edit Manager Details")

                        edit_company = st.text_input("COMPANY NAME *", value=manager['company_name'],
                                                     key=f"edit_company_{manager['id']}")
                        edit_email = st.text_input("EMAIL ID *", value=manager['email_id'],
                                                   key=f"edit_email_{manager['id']}")
                        edit_address = st.text_area("ADDRESS AND CONTACT *",
                                                    value=manager.get('address_and_contact', ''),
                                                    height=200, key=f"edit_address_{manager['id']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Save", key=f"save_btn_{manager['id']}",
                                         use_container_width=True, type="primary"):
                                if edit_company and edit_email and edit_address:
                                    success, message = db.update_manager(
                                        manager['id'],
                                        edit_company.strip(),
                                        edit_email.strip(),
                                        edit_address.strip()
                                    )
                                    if success:
                                        st.success(message)
                                        st.session_state[f"edit_mode_{manager['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                                else:
                                    st.warning("All fields required!")

                        with col2:
                            if st.button("❌ Cancel", key=f"cancel_btn_{manager['id']}", use_container_width=True):
                                st.session_state[f"edit_mode_{manager['id']}"] = False
                                st.rerun()

        # Table view
        st.markdown("---")
        st.subheader("📊 Table View")
        df = pd.DataFrame(managers)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

        display_columns = [col for col in ['id', 'company_name', 'email_id', 'address_and_contact', 'created_at']
                           if col in df.columns]
        st.dataframe(df[display_columns], use_container_width=True, hide_index=True)

        # Export
        st.markdown("---")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Managers')
        output.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name=f"managers_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("No managers found. Add managers using the tabs above.")


def show_bulk_upload_managers(db):
    """Bulk upload managers from Excel"""
    st.subheader("Upload Manager Details from Excel")

    st.info("""
    📋 **Excel File Requirements:**

    **Option 1: Column Position (Easiest)**
    - 1st Column = Company Name
    - 2nd Column = Email ID  
    - 3rd Column = Address and Contact

    **Option 2: Named Columns (Flexible)**
    - Any variation of: company name, email, address

    ✅ Case-insensitive, flexible format
    """)

    # Download template
    st.markdown("### 📥 Download Template")
    template_df = pd.DataFrame({
        'COMPANY NAME': ['ABC SHIPPING LTD', 'XYZ MARITIME CO'],
        'EMAIL ID': ['MANAGER@ABC.COM', 'ADMIN@XYZ.COM'],
        'ADDRESS AND CONTACT': [
            'DUBAI OFFICE, FLOOR 5, DUBAI, UAE\nCONTACT: +971 123 456 789',
            'ABU DHABI OFFICE, ABU DHABI, UAE\nCONTACT: +971 987 654 321'
        ]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name='Managers')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Template",
        data=output,
        file_name="manager_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with manager details",
        key="manager_upload"
    )

    if uploaded_file is not None:
        try:
            df_upload = pd.read_excel(uploaded_file)

            # Smart column mapping
            def smart_column_mapper(df):
                mapped_df = pd.DataFrame()
                columns = df.columns.tolist()

                # Strategy 1: Position-based
                if len(columns) >= 3:
                    mapped_df['COMPANY NAME'] = df.iloc[:, 0].astype(str).str.strip()
                    mapped_df['EMAIL ID'] = df.iloc[:, 1].astype(str).str.strip()
                    mapped_df['ADDRESS AND CONTACT'] = df.iloc[:, 2].astype(str).str.strip()

                    mapped_df = mapped_df.replace('nan', '')
                    mapped_df = mapped_df.replace('None', '')

                    return mapped_df, True, "position"

                # Strategy 2: Name-based
                company_col = email_col = address_col = None

                for col in columns:
                    col_clean = str(col).lower().replace('_', '').replace(' ', '').replace('-', '')

                    if any(kw in col_clean for kw in ['company', 'companyname', 'name', 'organization']):
                        if 'email' not in col_clean and 'address' not in col_clean:
                            company_col = col

                    if any(kw in col_clean for kw in ['email', 'emailid', 'mail']):
                        email_col = col

                    if any(kw in col_clean for kw in ['address', 'contact', 'addressandcontact', 'location']):
                        if email_col != col:
                            address_col = col

                if company_col and email_col and address_col:
                    mapped_df['COMPANY NAME'] = df[company_col].astype(str).str.strip()
                    mapped_df['EMAIL ID'] = df[email_col].astype(str).str.strip()
                    mapped_df['ADDRESS AND CONTACT'] = df[address_col].astype(str).str.strip()

                    mapped_df = mapped_df.replace('nan', '')
                    mapped_df = mapped_df.replace('None', '')

                    return mapped_df, True, "name"
                else:
                    missing = []
                    if not company_col: missing.append("Company Name")
                    if not email_col: missing.append("Email ID")
                    if not address_col: missing.append("Address")
                    return None, False, missing

            result = smart_column_mapper(df_upload)

            if result[1]:  # Success
                df_mapped = result[0]
                detection_method = result[2]

                # Show detection message
                if detection_method == "position":
                    st.success(f"✅ File uploaded! Detected {len(df_mapped)} records using column positions")
                else:
                    st.success(f"✅ File uploaded! Detected {len(df_mapped)} records using column names")

                # Quality check
                empty_company = (df_mapped['COMPANY NAME'] == '') | (df_mapped['COMPANY NAME'].isna())
                empty_email = (df_mapped['EMAIL ID'] == '') | (df_mapped['EMAIL ID'].isna())
                empty_address = (df_mapped['ADDRESS AND CONTACT'] == '') | (df_mapped['ADDRESS AND CONTACT'].isna())

                valid_rows = ~(empty_company | empty_email | empty_address)

                valid_count = valid_rows.sum()
                invalid_count = len(df_mapped) - valid_count

                # Show summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📋 Total Records", len(df_mapped))
                with col2:
                    st.metric("✅ Valid Records", valid_count)
                with col3:
                    if invalid_count > 0:
                        st.metric("⚠️ Invalid Records", invalid_count)
                    else:
                        st.metric("⚠️ Invalid Records", 0)

                if invalid_count > 0:
                    st.warning(f"⚠️ {invalid_count} record(s) have missing required fields and will be skipped")

                st.markdown("---")

                # Import button
                if valid_count > 0:
                    if st.button(f"📤 Import {valid_count} Valid Records", type="primary", use_container_width=True):
                        with st.spinner(f"Importing {valid_count} record(s)..."):
                            valid_data = df_mapped[valid_rows].copy()

                            managers_data = []
                            for idx, row in valid_data.iterrows():
                                managers_data.append({
                                    'COMPANY NAME': str(row['COMPANY NAME']).strip(),
                                    'EMAIL ID': str(row['EMAIL ID']).strip(),
                                    'ADDRESS AND CONTACT': str(row['ADDRESS AND CONTACT']).strip()
                                })

                            success_count, failed_records = db.insert_managers_bulk(managers_data)

                            # Show results
                            st.markdown("---")

                            if success_count > 0:
                                st.success(f"✅ Successfully imported {success_count} manager(s)!")

                                # Show imported records in a clean format
                                st.markdown("### 📋 Imported Managers:")
                                valid_imported = df_mapped[valid_rows].head(success_count)
                                for idx, row in valid_imported.iterrows():
                                    with st.expander(f"✅ {row['COMPANY NAME']}", expanded=False):
                                        st.write(f"**Email:** {row['EMAIL ID']}")
                                        st.text_area("Address & Contact", row['ADDRESS AND CONTACT'],
                                                     height=100, disabled=True, key=f"imported_{idx}")

                            if failed_records:
                                st.error(f"❌ Failed to import {len(failed_records)} record(s)")

                                # Show failed records
                                with st.expander("❌ Failed Records (Click to view)", expanded=False):
                                    for fail in failed_records:
                                        st.write(
                                            f"**Row {fail.get('row', 'N/A')}:** {fail.get('reason', 'Unknown error')}")
                                        if fail.get('company_name'):
                                            st.write(f"   - Company: {fail['company_name']}")
                                        if fail.get('email_id'):
                                            st.write(f"   - Email: {fail['email_id']}")
                                        st.markdown("---")

                            if success_count == len(managers_data):
                                st.balloons()
                else:
                    st.error("❌ No valid records to import!")
                    st.info("Please fix the errors in your Excel file and try again")

            else:  # Failed to detect columns
                missing_fields = result[2]
                st.error(f"❌ Could not detect required columns: {', '.join(missing_fields)}")
                st.warning("""
                **Please ensure your Excel file has:**
                1. At least 3 columns (1st=Company, 2nd=Email, 3rd=Address), OR
                2. Named columns with keywords like: 'company', 'email', 'address'
                """)

        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please make sure the file is a valid Excel file (.xlsx or .xls)")