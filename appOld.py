# appOld.py - Main Streamlit application

import streamlit as st
import pandas as pd
from database import VesselDatabase, initialize_database
from email_sender import EmailSender
from email_templates import get_html_template, get_plain_text_template
from config import DB_CONFIG, EMAIL_CONFIG, PORT_EMAIL_MAPPING, get_ports_by_country, get_all_countries
import os
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Vessel Management Dashboard",
    page_icon="🚢",
    layout="wide"
)

# Initialize database on first run
initialize_database()

# Initialize database and email sender
db = VesselDatabase()
email_sender = EmailSender()

# Sidebar navigation
st.sidebar.title("🚢 Vessel Dashboard")
menu = st.sidebar.radio(
    "Navigation",
    [
        "Insert Vessel Details",
        "View All Vessels",
        "Search Vessel",
        "Send Email to Vessels",
        "---",  # Separator
        "Add Manager Details",
        "View All Managers",
        "Send Email to Managers",
        "---",  # Separator
        "Generate Invoice",
        "Customize Invoice"
    ]
)

# ===========================
# 1. INSERT VESSEL DETAILS
# ===========================
if menu == "Insert Vessel Details":
    st.title("📝 Insert Vessel Details")

    # Add tabs for Manual Entry and Excel Upload
    tab1, tab2 = st.tabs(["✍️ Manual Entry", "📊 Upload Excel"])

    # TAB 1: MANUAL ENTRY
    with tab1:
        st.subheader("Enter Vessel Details Manually")

        vessel_name = st.text_input("Vessel Name *", placeholder="Enter vessel name")

        master_manager_email = st.text_area(
            "Master/Manager Email ID *",
            placeholder="Enter email addresses (one per line or comma-separated)\nExample:\nmaster@ship.com\nmanager@company.com\nor\nmaster@ship.com, manager@company.com",
            height=120
        )

        contact_details = st.text_area(
            "Contact Details",
            placeholder="Enter contact information:\n\nPhone Numbers:\n+971 123 456 789\n+971 987 654 321\n\nOffice Address:\nPort Office Building\nFloor 5, Suite 501\nDubai, UAE\n\nOther Information:\n...",
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
                st.warning("Please fill in all required fields (Vessel Name and Master/Manager Email)!")

    # TAB 2: EXCEL UPLOAD
    with tab2:
        st.subheader("Upload Vessel Details from Excel")

        st.info("""
        📋 **Excel File Format Requirements:**

        Your Excel file should have these columns (exact names):
        - **vessel_name** (Required)
        - **master_manager_email** (Required) - Can contain multiple emails separated by commas or newlines
        - **contact_details** (Optional) - Phone numbers, addresses, etc.

        **Example:**
        | vessel_name | master_manager_email | contact_details |
        |-------------|---------------------|-----------------|
        | Ship Alpha  | master1@ship.com, manager1@ship.com | Phone: +971123456789, Dubai Office |
        | Ship Beta   | master2@ship.com, manager2@ship.com | Phone: +971987654321, Abu Dhabi |
        """)

        # Download template button
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

        # Convert to Excel in memory
        from io import BytesIO

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

        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with vessel details"
        )

        # In the Excel upload tab, replace the validation section with this:

        if uploaded_file is not None:
            try:
                # Read Excel file
                df = pd.read_excel(uploaded_file)

                # Normalize column names (remove spaces, convert to lowercase)
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

                st.success(f"✅ File uploaded successfully! Found {len(df)} records.")

                # Show original column names
                st.info(f"📋 **Detected Columns:** {', '.join(df.columns.tolist())}")

                # Show preview
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)

                # Map alternative column names
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
                    'manager_email': 'master_manager_email',
                    'email_id': 'master_manager_email',
                    'emailid': 'master_manager_email',

                    'contact': 'contact_details',
                    'contacts': 'contact_details',
                    'contact_details': 'contact_details',
                    'contact_info': 'contact_details',
                    'details': 'contact_details',
                    'phone': 'contact_details'
                }

                # Rename columns based on mapping
                for old_name, new_name in column_mapping.items():
                    if old_name in df.columns:
                        df.rename(columns={old_name: new_name}, inplace=True)

                # Validate required columns
                required_columns = ['vessel_name', 'master_manager_email']
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                    st.warning("""
                    **Please make sure your Excel file has at least these columns:**
                    - Vessel Name (can be named: vessel_name, vessel, ship_name, ship, or name)
                    - Email (can be named: master_manager_email, email, emails, master_email, manager_email)
                    - Contact Details (optional: contact_details, contact, contacts, details)
                    """)
                else:
                    # Add contact_details column if not present
                    if 'contact_details' not in df.columns:
                        df['contact_details'] = ''

                    # Remove any extra columns, keep only the three we need
                    df = df[['vessel_name', 'master_manager_email', 'contact_details']]

                    # Show statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", len(df))
                    with col2:
                        st.metric("Valid Vessel Names", df['vessel_name'].notna().sum())
                    with col3:
                        st.metric("Valid Emails", df['master_manager_email'].notna().sum())

                    # Import button
                    if st.button("📤 Import to Database", type="primary", use_container_width=True):
                        with st.spinner("Importing data to database..."):
                            # Convert DataFrame to list of dictionaries
                            vessels_data = df.to_dict('records')

                            # Clean data (remove NaN values)
                            for vessel in vessels_data:
                                for key in vessel:
                                    if pd.isna(vessel[key]):
                                        vessel[key] = ''

                            # Insert into database
                            success_count, failed_records = db.insert_vessels_bulk(vessels_data)

                            # Show results
                            if success_count > 0:
                                st.success(f"✅ Successfully imported {success_count} vessel(s)!")

                            if failed_records:
                                st.warning(f"⚠️ Failed to import {len(failed_records)} record(s):")
                                failed_df = pd.DataFrame(failed_records)
                                st.dataframe(failed_df, use_container_width=True)

                            if success_count == len(vessels_data):
                                st.balloons()

            except Exception as e:
                st.error(f"❌ Error reading Excel file: {str(e)}")
                st.info("Please make sure the file is a valid Excel file (.xlsx or .xls)")

# ===========================
# 2. VIEW ALL VESSELS
# ===========================
elif menu == "View All Vessels":
    st.title("📋 All Vessel Details")

    vessels = db.get_all_vessels()

    if vessels:
        # Convert to DataFrame for better display
        df = pd.DataFrame(vessels)

        # Format created_at column if it exists
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Vessels", len(vessels))
        with col2:
            # Count vessels with emails
            email_count = df['master_manager_email'].notna().sum() if 'master_manager_email' in df.columns else 0
            st.metric("With Emails", email_count)

        st.markdown("---")

        # Display expandable cards for each vessel
        st.subheader("Vessel Details")
        for idx, vessel in enumerate(vessels):
            with st.expander(f"🚢 {vessel['vessel_name']}", expanded=False):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.write(f"**Vessel Name:**")
                    st.write(vessel['vessel_name'])
                    st.write(f"**Created At:**")
                    st.write(vessel.get('created_at', 'N/A'))

                with col2:
                    st.write(f"**Master/Manager Email:**")
                    st.text_area(
                        "Emails",
                        vessel.get('master_manager_email', ''),
                        height=100,
                        disabled=True,
                        key=f"view_email_{idx}"
                    )

                    if vessel.get('contact_details'):
                        st.write(f"**Contact Details:**")
                        st.text_area(
                            "Contact Info",
                            vessel['contact_details'],
                            height=150,
                            disabled=True,
                            key=f"view_contact_{idx}"
                        )

        st.markdown("---")

        # Also show as table
        st.subheader("📊 Table View")

        # Select columns to display
        display_columns = ['vessel_name', 'master_manager_email', 'contact_details']
        if 'created_at' in df.columns:
            display_columns.append('created_at')

        # Filter to only existing columns
        display_columns = [col for col in display_columns if col in df.columns]

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # Export to Excel
        st.markdown("---")
        st.subheader("📥 Export Data")

        try:
            from io import BytesIO

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Vessels')
            output.seek(0)

            st.download_button(
                label="📥 Download as Excel",
                data=output,
                file_name=f"vessel_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error creating Excel export: {str(e)}")

    else:
        st.info("No vessel details found in the database.")
        st.write("👉 Go to 'Insert Vessel Details' to add vessels.")

# ===========================
# 3. SEARCH VESSEL
# ===========================
elif menu == "Search Vessel":
    st.title("🔍 Search Vessel")

    search_term = st.text_input("Search by Vessel Name", placeholder="Enter vessel name to search")

    if search_term:
        results = db.search_vessel(search_term)

        if results:
            st.success(f"Found {len(results)} result(s)")

            for vessel in results:
                with st.expander(f"🚢 {vessel['vessel_name']}", expanded=True):
                    st.write(f"**Vessel Name:** {vessel['vessel_name']}")
                    st.write(f"**Created At:** {vessel['created_at']}")

                    st.write("**Master/Manager Email:**")
                    st.text_area(
                        "Emails",
                        vessel['master_manager_email'],
                        height=100,
                        disabled=True,
                        key=f"email_{vessel['id']}"
                    )

                    if vessel['contact_details']:
                        st.write("**Contact Details:**")
                        st.text_area(
                            "Contact Info",
                            vessel['contact_details'],
                            height=150,
                            disabled=True,
                            key=f"contact_{vessel['id']}"
                        )
        else:
            st.warning("No vessels found matching your search.")

# ===========================
# 4. SEND EMAIL
# ===========================
# In appOld.py - Update the Send Email section

elif menu == "Send Email to Vessels":
    st.title("📧 Send Email")

    # Two-step selection: First Country, then Port
    st.subheader("📍 Select Destination")

    col1, col2 = st.columns(2)

    with col1:
        # Get all countries
        countries = get_all_countries()
        selected_country = st.selectbox(
            "Select Country *",
            [""] + countries,
            format_func=lambda x: "-- Select Country --" if x == "" else x
        )

    with col2:
        # Get ports for selected country
        if selected_country:
            ports_by_country = get_ports_by_country()
            country_ports = ports_by_country.get(selected_country, [])
            port_options = [""] + [port['key'] for port in country_ports]

            selected_port = st.selectbox(
                "Select Port *",
                port_options,
                format_func=lambda x: "-- Select Port --" if x == "" else PORT_EMAIL_MAPPING[x]['portName']
            )
        else:
            st.selectbox("Select Port *", [""], format_func=lambda x: "Select a country first")
            selected_port = None

    # Show port details if selected
    if selected_port:
        port_details = PORT_EMAIL_MAPPING[selected_port]

        st.info(f"**Port:** {port_details['portName']}")
        st.info(f"**Country:** {port_details['country']}")

        # Display all attachments
        st.info(f"**Attachments ({len(port_details['attachments'])}):**")
        for idx, attachment in enumerate(port_details['attachments'], 1):
            st.write(f"   {idx}. {os.path.basename(attachment)}")

        # Email input method
        st.subheader("📧 Email Recipients")
        email_method = st.radio(
            "Choose input method:",
            ["Enter Email Manually", "Select by Vessel Name"]
        )

        recipient_emails = None

        if email_method == "Enter Email Manually":
            recipient_emails = st.text_area(
                "Recipient Emails *",
                placeholder="Enter email addresses (separate multiple emails with commas or new lines)",
                height=100
            )
        else:
            # Get all vessels for selection
            all_vessels = db.get_all_vessels()
            if all_vessels:
                vessel_names = [v['vessel_name'] for v in all_vessels]
                selected_vessel = st.selectbox("Select Vessel *", [""] + vessel_names)

                if selected_vessel:
                    vessel_data = db.get_vessel_by_name(selected_vessel)
                    if vessel_data:
                        st.text_area(
                            "Master/Manager Email",
                            vessel_data['master_manager_email'],
                            height=100,
                            disabled=True
                        )

                        if vessel_data['contact_details']:
                            st.text_area(
                                "Contact Details",
                                vessel_data['contact_details'],
                                height=150,
                                disabled=True
                            )

                        recipient_emails = st.text_area(
                            "Recipient Emails *",
                            value=vessel_data['master_manager_email'],
                            placeholder="Edit emails or add more (comma-separated)",
                            height=100
                        )
            else:
                st.warning("No vessels found in database. Please add vessels first.")

        # Email content preview
        st.subheader("📄 Email Content")
        email_subject = st.text_input("Subject", value=port_details['subject'])

        # Template preview options
        preview_format = st.radio("Preview Format:", ["HTML Preview", "Plain Text"])

        if preview_format == "HTML Preview":
            st.info("📧 **HTML Email Preview** (Email will be sent with professional formatting)")
            html_preview = get_html_template(port_details['portName'], port_details['country'])

            # Show HTML in an expander
            with st.expander("Click to view HTML Email Preview", expanded=False):
                st.components.v1.html(html_preview, height=800, scrolling=True)
        else:
            st.info("📄 **Plain Text Email Preview** (Fallback version for basic email clients)")
            plain_preview = get_plain_text_template(port_details['portName'], port_details['country'])
            st.text_area("Plain Text Version", plain_preview, height=400, disabled=True)

        # Send button
        st.markdown("---")
        if st.button("📨 Send Email", type="primary", use_container_width=True):
            if recipient_emails and email_subject:
                # Check if all attachments exist
                missing_attachments = [att for att in port_details['attachments'] if not os.path.exists(att)]

                if missing_attachments:
                    st.error("❌ Missing attachment files:")
                    for att in missing_attachments:
                        st.write(f"- {att}")
                else:
                    with st.spinner(f"Sending HTML emails with {len(port_details['attachments'])} attachment(s)..."):
                        success_count, failed_emails, results = email_sender.send_email_to_multiple_html(
                            recipient_emails=recipient_emails,
                            subject=email_subject,
                            port_name=port_details['portName'],
                            country=port_details['country'],
                            attachment_paths=port_details['attachments']  # Pass list of attachments
                        )

                        # Display results
                        if success_count > 0:
                            st.success(
                                f"✅ Successfully sent {success_count} HTML email(s) with {len(port_details['attachments'])} attachment(s) each!")

                        if failed_emails:
                            st.error(f"❌ Failed to send to {len(failed_emails)} email(s):")
                            for email in failed_emails:
                                st.write(f"- {email}")

                        # Show detailed results
                        with st.expander("View Detailed Results"):
                            for result in results:
                                if result['status'] == 'Success':
                                    st.write(f"✅ {result['email']}: {result['status']}")
                                else:
                                    st.write(f"❌ {result['email']}: {result['status']}")

                        if success_count == len(results):
                            st.balloons()
            else:
                st.warning("Please fill in all required fields!")
    else:
        st.info("👆 Please select a country and port to continue")

# ===========================
# 5. ADD MANAGER DETAILS
# ===========================
elif menu == "Add Manager Details":
    st.title("👔 Add Manager Details")

    # Add tabs for Manual Entry and Excel Upload
    tab1, tab2 = st.tabs(["✍️ Manual Entry", "📊 Upload Excel"])

    # TAB 1: MANUAL ENTRY
    with tab1:
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

    # TAB 2: EXCEL UPLOAD (SMART COLUMN DETECTION)
    with tab2:
        st.subheader("Upload Manager Details from Excel")

        st.info("""
        📋 **Excel File Requirements:**

        **Option 1: Column Position (Easiest)**
        - 1st Column = Company Name
        - 2nd Column = Email ID  
        - 3rd Column = Address and Contact
        *(Column headers don't matter, we use position)*

        **Option 2: Named Columns (Flexible)**
        - Column names can be in ANY format:
          - `Company Name`, `COMPANY NAME`, `company_name`, `CompanyName`
          - `Email`, `EMAIL ID`, `email_id`, `Email Address`
          - `Address`, `ADDRESS AND CONTACT`, `address_and_contact`, `Contact Details`

        ✅ Both uppercase and lowercase accepted
        ✅ Underscores, spaces, or no separators accepted
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

                st.success(f"✅ File uploaded successfully! Found {len(df_upload)} records.")
                st.markdown("#### 📄 Uploaded Data Preview")
                st.dataframe(df_upload.head(10), use_container_width=True)


                # SMART COLUMN MAPPING FUNCTION
                def smart_column_mapper(df):
                    """
                    Intelligently map columns to required fields
                    Priority:
                    1. Column position (1st, 2nd, 3rd)
                    2. Column name matching (case-insensitive, flexible)
                    """
                    mapped_df = pd.DataFrame()

                    # Get list of columns
                    columns = df.columns.tolist()

                    # Strategy 1: Use column position if we have at least 3 columns
                    if len(columns) >= 3:
                        st.info("📊 Detecting columns by position (1st=Company, 2nd=Email, 3rd=Address)")
                        mapped_df['COMPANY NAME'] = df.iloc[:, 0]
                        mapped_df['EMAIL ID'] = df.iloc[:, 1]
                        mapped_df['ADDRESS AND CONTACT'] = df.iloc[:, 2]
                        return mapped_df, True

                    # Strategy 2: Try to match by column names (flexible)
                    st.info("📊 Detecting columns by name (case-insensitive)")

                    company_col = None
                    email_col = None
                    address_col = None

                    for col in columns:
                        col_clean = col.lower().replace('_', '').replace(' ', '').replace('-', '')

                        # Match Company Name
                        if any(keyword in col_clean for keyword in ['company', 'companyname', 'name', 'organization']):
                            if 'email' not in col_clean and 'address' not in col_clean:
                                company_col = col

                        # Match Email
                        if any(keyword in col_clean for keyword in ['email', 'emailid', 'emailaddress', 'mail']):
                            email_col = col

                        # Match Address
                        if any(keyword in col_clean for keyword in
                               ['address', 'contact', 'addressandcontact', 'location', 'office']):
                            if email_col != col:  # Don't use email column for address
                                address_col = col

                    # Check if we found all required columns
                    if company_col and email_col and address_col:
                        st.success(f"✅ Detected: Company='{company_col}', Email='{email_col}', Address='{address_col}'")
                        mapped_df['COMPANY NAME'] = df[company_col]
                        mapped_df['EMAIL ID'] = df[email_col]
                        mapped_df['ADDRESS AND CONTACT'] = df[address_col]
                        return mapped_df, True
                    else:
                        missing = []
                        if not company_col:
                            missing.append("Company Name")
                        if not email_col:
                            missing.append("Email ID")
                        if not address_col:
                            missing.append("Address and Contact")

                        return None, False, missing


                # Apply smart mapping
                result = smart_column_mapper(df_upload)

                if result[1]:  # Success
                    df_mapped = result[0]

                    st.markdown("---")
                    st.markdown("#### ✅ Mapped Data (Ready for Import)")
                    st.dataframe(df_mapped.head(10), use_container_width=True)

                    # Show statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", len(df_mapped))
                    with col2:
                        valid_count = df_mapped[['COMPANY NAME', 'EMAIL ID', 'ADDRESS AND CONTACT']].notna().all(
                            axis=1).sum()
                        st.metric("Valid Records", valid_count)
                    with col3:
                        invalid_count = len(df_mapped) - valid_count
                        st.metric("Invalid Records", invalid_count)

                    if invalid_count > 0:
                        st.warning(f"⚠️ {invalid_count} record(s) have missing required fields and will be skipped.")

                    # Import button
                    if st.button("📤 Import to Database", type="primary", use_container_width=True,
                                 key="import_managers"):
                        with st.spinner("Importing data..."):
                            # Prepare data for import
                            managers_data = []
                            skipped_count = 0

                            for idx, row in df_mapped.iterrows():
                                # Check if all required fields are present
                                if pd.notna(row['COMPANY NAME']) and pd.notna(row['EMAIL ID']) and pd.notna(
                                        row['ADDRESS AND CONTACT']):
                                    managers_data.append({
                                        'COMPANY NAME': str(row['COMPANY NAME']).strip(),
                                        'EMAIL ID': str(row['EMAIL ID']).strip(),
                                        'ADDRESS AND CONTACT': str(row['ADDRESS AND CONTACT']).strip()
                                    })
                                else:
                                    skipped_count += 1

                            if managers_data:
                                success_count, failed_records = db.insert_managers_bulk(managers_data)

                                # Show results
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.success(f"✅ Imported: {success_count}")
                                with col2:
                                    if failed_records:
                                        st.error(f"❌ Failed: {len(failed_records)}")
                                with col3:
                                    if skipped_count > 0:
                                        st.warning(f"⚠️ Skipped: {skipped_count}")

                                if failed_records:
                                    with st.expander("❌ Failed Records Details", expanded=False):
                                        st.dataframe(pd.DataFrame(failed_records), use_container_width=True)

                                if success_count == len(managers_data):
                                    st.balloons()
                            else:
                                st.error("❌ No valid records to import!")

                else:  # Failed to map
                    missing_fields = result[2]
                    st.error(f"❌ Could not detect required columns: {', '.join(missing_fields)}")
                    st.warning("""
                    **Please ensure your Excel file has:**
                    1. At least 3 columns (1st=Company, 2nd=Email, 3rd=Address), OR
                    2. Named columns containing keywords: 'company', 'email', 'address'
                    """)

                    st.markdown("#### Available Columns in Your File:")
                    for idx, col in enumerate(df_upload.columns, 1):
                        st.write(f"{idx}. `{col}`")

            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please make sure the file is a valid Excel file (.xlsx or .xls)")

# ===========================
# 6. VIEW & SEARCH MANAGERS (COMBINED)
# ===========================
elif menu == "View All Managers":
    st.title("📋 Manager Management")

    # Search bar at the top
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search by Company Name, Email, or Address", placeholder="Type to search...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear Search", use_container_width=True):
            search_term = ""
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

        # Display managers in cards with edit/delete options
        for idx, manager in enumerate(managers):
            with st.expander(f"🏢 {manager['company_name']}", expanded=False):
                # Display mode by default
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

                    # Confirm delete dialog
                    if st.session_state.get(f"confirm_delete_{manager['id']}", False):
                        st.warning(f"⚠️ Are you sure you want to delete **{manager['company_name']}**?")
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_yes_{manager['id']}", type="primary"):
                                success, message = db.delete_manager(manager['id'])
                                if success:
                                    st.success(message)
                                    del st.session_state[f"confirm_delete_{manager['id']}"]
                                    st.rerun()
                                else:
                                    st.error(message)
                        with col2:
                            if st.button("Cancel", key=f"confirm_no_{manager['id']}"):
                                del st.session_state[f"confirm_delete_{manager['id']}"]
                                st.rerun()
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
                        if st.button("💾 Save Changes", key=f"save_btn_{manager['id']}",
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
                                st.warning("All fields are required!")

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
        st.info("No managers found. Add managers in the 'Add Manager Details' tab.")

# ===========================
# 7. SEND EMAIL TO MANAGERS (UPDATED WITH RICH TEXT EDITOR)
# ===========================
elif menu == "Send Email to Managers":
    st.title("📧 Send Email to Managers")

    # Email format selection
    email_format = st.radio(
        "Select Email Format:",
        ["HTML Template", "Custom Email (Rich Text Editor)"],
        horizontal=True
    )

    st.markdown("---")

    # Recipient selection
    st.subheader("📧 Select Recipients")

    selection_method = st.radio(
        "Choose method:",
        ["Enter Email Manually", "Select by Company Name(s)", "Select All Managers"]
    )

    recipient_emails = None

    if selection_method == "Enter Email Manually":
        recipient_emails = st.text_area(
            "Recipient Emails *",
            placeholder="Enter email addresses (comma or newline separated)\nExample:\nmanager@company.com\nadmin@company.com",
            height=150
        )
    elif selection_method == "Select All Managers":
        all_managers = db.get_all_managers()
        if all_managers:
            all_emails = [m['email_id'] for m in all_managers]
            recipient_emails = '\n'.join(all_emails)
            st.success(f"✅ Selected all {len(all_managers)} managers")
            st.text_area("Recipient Emails", recipient_emails, height=200, disabled=True)
        else:
            st.warning("No managers found.")
    else:  # Select by Company Name(s)
        all_managers = db.get_all_managers()
        if all_managers:
            st.info("💡 Select multiple companies. All their emails will be included.")

            company_names = [m['company_name'] for m in all_managers]
            search_company = st.text_input("🔍 Search Companies", placeholder="Type to filter...")

            filtered_companies = [name for name in company_names if
                                  not search_company or search_company.lower() in name.lower()]
            st.write(f"Found {len(filtered_companies)} company(ies)")

            selected_companies = st.multiselect("Select Company(ies) *", filtered_companies)

            if selected_companies:
                st.success(f"✅ Selected {len(selected_companies)} company(ies)")

                all_emails = []
                company_details = []

                for company in selected_companies:
                    manager = next((m for m in all_managers if m['company_name'] == company), None)
                    if manager:
                        all_emails.append(manager['email_id'])
                        company_details.append({
                            'company': company,
                            'email': manager['email_id']
                        })

                st.subheader("📋 Selected Companies")
                for idx, cd in enumerate(company_details, 1):
                    st.write(f"{idx}. 🏢 **{cd['company']}** - {cd['email']}")

                recipient_emails = '\n'.join(all_emails)

                st.markdown("---")
                recipient_emails = st.text_area(
                    "Recipient Emails * (Edit if needed)",
                    value=recipient_emails,
                    height=150
                )

                if recipient_emails:
                    email_list = [e.strip() for e in recipient_emails.replace(';', ',').replace('\n', ',').split(',')
                                  if e.strip()]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Emails", len(email_list))
                    with col2:
                        st.metric("Unique Emails", len(set(email_list)))
        else:
            st.warning("No managers found.")

    # Email content
    st.markdown("---")
    st.subheader("📄 Email Content")

    email_subject = st.text_input("Subject *", value="Business Communication from NexBay International")

    if email_format == "HTML Template":
        # Use existing template
        st.markdown("### 📧 Email Preview")
        from manager_email_templates import get_manager_html_template

        html_preview = get_manager_html_template()
        with st.expander("Click to view HTML Preview", expanded=False):
            st.components.v1.html(html_preview, height=800, scrolling=True)

        email_body_html = html_preview
        email_body_plain = None

    else:
        # Rich text editor
        st.markdown("### ✍️ Compose Your Email")

        # Text formatting toolbar
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            font_size = st.selectbox("Font Size", [10, 12, 14, 16, 18, 20, 24], index=2)
        with col2:
            text_color = st.color_picker("Text Color", "#000000")
        with col3:
            bold = st.checkbox("Bold")
        with col4:
            italic = st.checkbox("Italic")
        with col5:
            underline = st.checkbox("Underline")

        # Email body editor
        email_body = st.text_area(
            "Email Body *",
            placeholder="Type your email message here...\n\nYou can format it using the options above.",
            height=400,
            key="custom_email_body"
        )

        # Add signature option
        add_signature = st.checkbox("Add Company Signature", value=True)

        # Generate HTML from text
        if email_body:
            style = f"font-size: {font_size}px; color: {text_color};"
            if bold:
                style += " font-weight: bold;"
            if italic:
                style += " font-style: italic;"
            if underline:
                style += " text-decoration: underline;"

            # Convert plain text to HTML with line breaks
            formatted_body = email_body.replace('\n', '<br>')

            signature = """
            <br><br>
            <div style="border-top: 2px solid #0066cc; padding-top: 15px; margin-top: 20px;">
                <p style="margin: 5px 0;"><strong style="color: #0066cc;">NexBay International LLC</strong></p>
                <p style="margin: 5px 0; font-style: italic; color: #666;">Moving Your Fleet Forward....</p>
                <p style="margin: 5px 0; font-size: 13px;">📧 info@nxbay.com | stores@nxbay.com</p>
                <p style="margin: 5px 0; font-size: 13px;">📞 +971 56 961 0203</p>
                <p style="margin: 5px 0; font-size: 13px;">🌐 www.nxbay.com</p>
                <p style="margin: 5px 0; font-size: 13px;">📍 Media City, Al Massaned, Al Bataeh, Sharjah, UAE</p>
            </div>
            """ if add_signature else ""

            email_body_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
                <div style="{style}">
                    {formatted_body}
                </div>
                {signature}
            </body>
            </html>
            """

            email_body_plain = email_body

            # Preview
            st.markdown("### 📧 Email Preview")
            with st.expander("Click to view Email Preview", expanded=False):
                st.components.v1.html(email_body_html, height=600, scrolling=True)
        else:
            email_body_html = None
            email_body_plain = None

    # Send button
    st.markdown("---")
    if st.button("📨 Send Email", type="primary", use_container_width=True):
        if recipient_emails and email_subject and (email_body_html or email_body_plain):
            email_list = [e.strip() for e in recipient_emails.replace(';', ',').replace('\n', ',').split(',')
                          if e.strip()]

            if not email_list:
                st.error("❌ No valid emails!")
            else:
                st.info(f"📧 Sending to {len(email_list)} recipient(s)...")

                with st.spinner("Sending emails..."):
                    success_count = 0
                    failed_emails = []
                    results = []

                    for email in email_list:
                        try:
                            if email_format == "HTML Template":
                                from manager_email_templates import get_manager_plain_text_template

                                plain_body = get_manager_plain_text_template()

                                success, msg = email_sender.send_email_html(
                                    recipient_email=email,
                                    subject=email_subject,
                                    html_body=email_body_html,
                                    plain_text_body=plain_body,
                                    attachment_paths=None
                                )
                            else:
                                success, msg = email_sender.send_email_html(
                                    recipient_email=email,
                                    subject=email_subject,
                                    html_body=email_body_html,
                                    plain_text_body=email_body_plain,
                                    attachment_paths=None
                                )

                            if success:
                                success_count += 1
                                results.append({'email': email, 'status': 'Success'})
                            else:
                                failed_emails.append(email)
                                results.append({'email': email, 'status': f'Failed: {msg}'})
                        except Exception as e:
                            failed_emails.append(email)
                            results.append({'email': email, 'status': f'Failed: {str(e)}'})

                    # Show results
                    col1, col2 = st.columns(2)
                    with col1:
                        if success_count > 0:
                            st.success(f"✅ Successfully sent: {success_count}")
                    with col2:
                        if failed_emails:
                            st.error(f"❌ Failed: {len(failed_emails)}")

                    with st.expander("📊 Detailed Results", expanded=len(failed_emails) > 0):
                        for r in results:
                            if r['status'] == 'Success':
                                st.write(f"✅ {r['email']}: {r['status']}")
                            else:
                                st.write(f"❌ {r['email']}: {r['status']}")

                    if success_count == len(results):
                        st.balloons()
        else:
            st.warning("⚠️ Please fill all required fields!")
# ===========================
# GENERATE INVOICE
# ===========================
elif menu == "Generate Invoice":
    st.title("📄 Generate Invoice & Delivery Note")

    # Get last invoice number
    last_invoice = db.get_last_invoice_number()

    if last_invoice:
        st.info(f"📋 Last Invoice Number: **{last_invoice}**")
        try:
            last_num = int(last_invoice)
            suggested_invoice = str(last_num + 1)
        except:
            suggested_invoice = ""
    else:
        st.info("📋 No previous invoices found")
        suggested_invoice = "26010"

    st.markdown("---")

    # Invoice details input
    col1, col2 = st.columns(2)

    with col1:
        invoice_number = st.text_input(
            "Invoice Number *",
            value=suggested_invoice,
            help="You can edit this number"
        )

        vessel_name = st.text_input("Vessel Name *", placeholder="Enter vessel name")

        invoice_type = st.selectbox(
            "Invoice Type *",
            ["PVT provision", "Ship provision", "Bonded Stores", "Technical Stores"]
        )

    with col2:
        port_of_delivery = st.text_input("Port of Delivery *", placeholder="e.g., Fujairah Port")

        currency = st.radio("Currency *", ["USD", "AED"], horizontal=True)

        output_format = st.multiselect(
            "Output Format *",
            ["PDF", "Word"],
            default=["PDF", "Word"]
        )

    st.markdown("---")

    # Excel upload
    st.subheader("📊 Upload Items Excel")

    st.info("""
    **Required Excel Columns:**
    - Item No.
    - Item Description
    - Quantity
    - UoM Code
    - Unit Price
    """)

    # Download template
    template_df = pd.DataFrame({
        'Item No.': ['ABS-13935', 'ABS-4913'],
        'Item Description': ['BAVARIA-NON-ALCOHOLIC BEER-24X500ML-CTN', 'COCA COLA SOFT DRINKS 24X300ML CTN'],
        'Quantity': [2, 2],
        'UoM Code': ['EA', 'CTN'],
        'Unit Price': [35.8, 18.1]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name='Items')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Template",
        data=output,
        file_name="invoice_items_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'], key="invoice_excel")

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()

            st.success(f"✅ File uploaded! Found {len(df)} items")
            st.dataframe(df, use_container_width=True)

            required_cols = ['Item No.', 'Item Description', 'Quantity', 'UoM Code', 'Unit Price']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
            else:
                df_preview = df.copy()
                df_preview['Total'] = df_preview['Quantity'] * df_preview['Unit Price']
                grand_total = df_preview['Total'].sum()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Items", len(df))
                with col2:
                    st.metric("Total Quantity", int(df['Quantity'].sum()))
                with col3:
                    st.metric(f"Grand Total ({currency})", f"{grand_total:.2f}")

                st.markdown("---")

                # Generate button
                if st.button("🚀 Generate Invoice & Delivery Note", type="primary", use_container_width=True):
                    if invoice_number and vessel_name and port_of_delivery:
                        with st.spinner("Generating combined documents..."):
                            from invoice_generator import generate_combined_word, generate_combined_pdf

                            invoice_data = {
                                'invoice_number': invoice_number,
                                'vessel_name': vessel_name,
                                'port_of_delivery': port_of_delivery,
                                'invoice_type': invoice_type,
                                'currency': currency
                            }

                            # Generate documents
                            generated_files = []

                            try:
                                if "Word" in output_format:
                                    # Combined Word document
                                    combined_word, total = generate_combined_word(df.copy(), invoice_data)
                                    generated_files.append(('combined_word', combined_word, total))

                                if "PDF" in output_format:
                                    # Combined PDF document
                                    combined_pdf, total = generate_combined_pdf(df.copy(), invoice_data)
                                    generated_files.append(('combined_pdf', combined_pdf, total))

                                # Save to database
                                success, msg = db.insert_invoice(
                                    invoice_number, vessel_name, port_of_delivery,
                                    invoice_type, currency, generated_files[0][2]
                                )

                                if success:
                                    st.success("✅ Documents generated and saved to database!")
                                else:
                                    st.warning(f"⚠️ Documents generated but database save failed: {msg}")

                                # Download buttons
                                st.subheader("📥 Download Generated Documents")
                                st.info("💡 Each document contains both Invoice and Delivery Note")

                                col1, col2 = st.columns(2)

                                for file_type, file_data, _ in generated_files:
                                    if file_type == 'combined_word':
                                        with col1:
                                            st.download_button(
                                                label="📄 Download Word (Invoice + Delivery Note)",
                                                data=file_data,
                                                file_name=f"Invoice_DN_{invoice_number}.docx",
                                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                use_container_width=True
                                            )
                                    elif file_type == 'combined_pdf':
                                        with col2:
                                            st.download_button(
                                                label="📕 Download PDF (Invoice + Delivery Note)",
                                                data=file_data,
                                                file_name=f"Invoice_DN_{invoice_number}.pdf",
                                                mime="application/pdf",
                                                use_container_width=True
                                            )

                                st.balloons()

                            except FileNotFoundError as e:
                                st.error(f"❌ {str(e)}")
                                st.info("Please make sure 'invoice_template.docx' is in the 'templates' folder")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please fill in all required fields!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
# ===========================
# 6. CUSTOMIZE INVOICE (Placeholder)
# ===========================
elif menu == "Customize Invoice":
    st.title("⚙️ Customize Invoice")
    st.info("This feature will allow you to customize invoice templates.")

    st.warning("Customization feature coming soon!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Vessel Management System v1.0**")
# st.sidebar.markdown("Made with ❤️ using Streamlit")