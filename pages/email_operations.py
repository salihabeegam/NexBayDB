# pages/email_operations.py
import streamlit as st
from email_sender import EmailSender
from email_templates import get_html_template, get_plain_text_template
from config import PORT_EMAIL_MAPPING, get_ports_by_country, get_all_countries
import os

email_sender = EmailSender()

# BCC email constant
BCC_EMAIL = "nexbayinternational@gmail.com"


def show_manager_email_page(db):
    """Send email to managers"""
    st.subheader("📧 Send Email to Managers")

    # Import manager email template
    try:
        from manager_email_templates import get_manager_html_template, get_manager_plain_text_template
    except:
        st.error("Manager email templates not found")
        return

    # Email format
    email_format = st.radio("Select Email Format:", ["HTML Template", "Custom Email (Rich Text Editor)"],
                            horizontal=True)
    st.markdown("---")

    # Recipient selection
    st.subheader("📧 Select Recipients")
    selection_method = st.radio("Choose method:",
                                ["Enter Email Manually", "Select by Company Name(s)", "Select All Managers"])

    recipient_emails = None

    if selection_method == "Enter Email Manually":
        recipient_emails = st.text_area("Recipient Emails *", placeholder="Enter emails (comma or newline separated)",
                                        height=150)

    elif selection_method == "Select All Managers":
        all_managers = db.get_all_managers()
        if all_managers:
            all_emails = [m['email_id'] for m in all_managers]
            recipient_emails = '\n'.join(all_emails)
            st.success(f"✅ Selected all {len(all_managers)} managers")
            st.text_area("Recipient Emails", recipient_emails, height=200, disabled=True)
        else:
            st.warning("No managers found.")

    else:  # Select by company
        all_managers = db.get_all_managers()
        if all_managers:
            company_names = [m['company_name'] for m in all_managers]
            selected_companies = st.multiselect("Select Company(ies) *", company_names)

            if selected_companies:
                all_emails = [m['email_id'] for m in all_managers if m['company_name'] in selected_companies]
                recipient_emails = '\n'.join(all_emails)
                st.text_area("Recipient Emails", recipient_emails, height=150)

    # Email content
    st.markdown("---")
    st.subheader("📄 Email Content")
    email_subject = st.text_input("Subject *", value="Business Communication from NexBay International")

    # Attachments - COMMON FOR BOTH FORMATS
    st.markdown("### 📎 Attachments (Optional)")
    uploaded_files = st.file_uploader(
        "Upload attachments",
        type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'txt', 'zip'],
        accept_multiple_files=True,
        help="You can upload multiple files"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) attached")
        for file in uploaded_files:
            st.write(f"📎 {file.name} ({file.size / 1024:.1f} KB)")

    if email_format == "HTML Template":
        st.markdown("### 📧 Email Preview")
        html_preview = get_manager_html_template()
        with st.expander("Click to view HTML Preview", expanded=False):
            st.components.v1.html(html_preview, height=800, scrolling=True)
        email_body_html = html_preview
        email_body_plain = get_manager_plain_text_template()

    else:  # Custom Email with Rich Text Editor
        st.markdown("### ✍️ Compose Your Email")

        # Text formatting toolbar
        st.markdown("#### 🎨 Text Formatting")
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            font_family = st.selectbox("Font",
                                       ["Arial", "Times New Roman", "Courier New", "Georgia", "Verdana", "Helvetica"],
                                       index=0)
        with col2:
            font_size = st.selectbox("Size", [10, 12, 14, 16, 18, 20, 24, 28, 32, 36], index=2)
        with col3:
            text_color = st.color_picker("Text Color", "#000000")
        with col4:
            bg_color = st.color_picker("Highlight", "#ffffff")
        with col5:
            st.write("")
            st.write("")
            bold = st.checkbox("**Bold**")
        with col6:
            st.write("")
            st.write("")
            italic = st.checkbox("*Italic*")

        col7, col8, col9 = st.columns(3)
        with col7:
            underline = st.checkbox("Underline")
        with col8:
            align = st.selectbox("Align", ["Left", "Center", "Right", "Justify"])
        with col9:
            line_height = st.selectbox("Line Spacing", ["1.0", "1.15", "1.5", "2.0"], index=2)

        # Email body editor
        st.markdown("#### 📝 Email Body")
        email_body = st.text_area(
            "Type your email message here *",
            placeholder="Dear Valued Partner,\n\nWe are pleased to inform you...\n\nBest regards,\nNexBay International Team",
            height=400,
            key="custom_email_body_manager"
        )

        # Additional options
        col1, col2 = st.columns(2)
        with col1:
            add_signature = st.checkbox("Add Company Signature", value=True)
        with col2:
            add_logo = st.checkbox("Add Company Logo", value=False)

        # Generate HTML from formatted text
        if email_body:
            # Build style
            style = f"font-family: {font_family}; font-size: {font_size}px; color: {text_color};"
            if bg_color != "#ffffff":
                style += f" background-color: {bg_color};"
            if bold:
                style += " font-weight: bold;"
            if italic:
                style += " font-style: italic;"
            if underline:
                style += " text-decoration: underline;"

            # Text alignment
            text_align = align.lower()
            style += f" text-align: {text_align}; line-height: {line_height};"

            # Convert plain text to HTML with line breaks
            formatted_body = email_body.replace('\n', '<br>')

            # Logo
            logo_html = ""
            if add_logo:
                logo_html = """
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #0066cc; margin: 0;">⚓ NexBay International LLC</h2>
                    <p style="color: #666; font-style: italic; margin: 5px 0;">Moving Your Fleet Forward....</p>
                </div>
                <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
                """

            # Signature
            signature = ""
            if add_signature:
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
                """

            email_body_html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto;">
                {logo_html}
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

    # BCC notification
    st.info(f"ℹ️ **Note:** All emails will be BCC'd to {BCC_EMAIL}")

    # Send button
    st.markdown("---")
    if st.button("📨 Send Email", type="primary", use_container_width=True, key="send_manager_email"):
        if recipient_emails and email_subject and (email_body_html or email_body_plain):
            email_list = [e.strip() for e in recipient_emails.replace(';', ',').replace('\n', ',').split(',') if
                          e.strip()]

            if not email_list:
                st.error("❌ No valid emails!")
            else:
                # Prepare attachments
                attachment_paths = []
                if uploaded_files:
                    import tempfile
                    temp_dir = tempfile.mkdtemp()
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        attachment_paths.append(file_path)

                st.info(f"📧 Sending to {len(email_list)} recipient(s)...")

                with st.spinner("Sending emails..."):
                    success_count = 0
                    failed_emails = []
                    results = []

                    for email in email_list:
                        try:
                            success, msg = email_sender.send_email_html(
                                recipient_email=email,
                                subject=email_subject,
                                html_body=email_body_html,
                                plain_text_body=email_body_plain,
                                attachment_paths=attachment_paths,
                                bcc_email=BCC_EMAIL
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

                    # Cleanup temp files
                    if attachment_paths:
                        import shutil
                        try:
                            shutil.rmtree(temp_dir)
                        except:
                            pass
        else:
            st.warning("⚠️ Please fill all required fields!")


def show_vessel_email_page(db):
    """Send email to vessels - WITH MULTIPLE VESSEL SELECTION"""
    st.subheader("📧 Send Email to Vessels")

    # Country & Port selection
    col1, col2 = st.columns(2)

    with col1:
        countries = get_all_countries()
        selected_country = st.selectbox("Select Country *", [""] + countries,
                                        format_func=lambda x: "-- Select Country --" if x == "" else x)

    with col2:
        if selected_country:
            ports_by_country = get_ports_by_country()
            country_ports = ports_by_country.get(selected_country, [])
            port_options = [""] + [port['key'] for port in country_ports]

            selected_port = st.selectbox("Select Port *", port_options,
                                         format_func=lambda x: "-- Select Port --" if x == "" else
                                         PORT_EMAIL_MAPPING[x]['portName'])
        else:
            st.selectbox("Select Port *", [""], format_func=lambda x: "Select a country first")
            selected_port = None

    if selected_port:
        port_details = PORT_EMAIL_MAPPING[selected_port]
        st.info(f"**Port:** {port_details['portName']}")
        st.info(f"**Default Attachments:** {len(port_details['attachments'])}")

        # Email recipients - MULTIPLE SELECTION
        st.markdown("---")
        st.subheader("📧 Email Recipients")
        email_method = st.radio("Choose input method:",
                                ["Enter Email Manually", "Select by Vessel Name(s)", "Select All Vessels"])

        recipient_emails = None

        if email_method == "Enter Email Manually":
            recipient_emails = st.text_area("Recipient Emails *",
                                            placeholder="Enter emails (comma or newline separated)",
                                            height=150)

        elif email_method == "Select All Vessels":
            all_vessels = db.get_all_vessels()
            if all_vessels:
                all_emails = []
                for vessel in all_vessels:
                    if vessel.get('master_manager_email'):
                        vessel_emails = vessel['master_manager_email'].replace(',', '\n').replace(';', '\n').split('\n')
                        all_emails.extend([e.strip() for e in vessel_emails if e.strip()])

                recipient_emails = '\n'.join(all_emails)
                st.success(f"✅ Selected all {len(all_vessels)} vessels ({len(all_emails)} email addresses)")
                st.text_area("Recipient Emails", recipient_emails, height=200, disabled=True)
            else:
                st.warning("No vessels found.")

        else:  # Select by Vessel Name(s)
            all_vessels = db.get_all_vessels()
            if all_vessels:
                st.info("💡 **You can select multiple vessels**. All their emails will be combined.")

                vessel_names = [v['vessel_name'] for v in all_vessels]
                search_vessel = st.text_input("🔍 Search Vessels", placeholder="Type to filter vessels...")

                if search_vessel:
                    filtered_vessels = [name for name in vessel_names if search_vessel.lower() in name.lower()]
                    st.write(f"Found {len(filtered_vessels)} vessel(s)")
                else:
                    filtered_vessels = vessel_names

                selected_vessels = st.multiselect(
                    "Select Vessel(s) *",
                    filtered_vessels,
                    help="You can select multiple vessels"
                )

                if selected_vessels:
                    st.success(f"✅ Selected {len(selected_vessels)} vessel(s)")

                    all_emails = []
                    vessel_details_list = []

                    for vessel_name in selected_vessels:
                        vessel_data = db.get_vessel_by_name(vessel_name)
                        if vessel_data and vessel_data.get('master_manager_email'):
                            vessel_emails = vessel_data['master_manager_email'].replace(',', '\n').replace(';',
                                                                                                           '\n').split(
                                '\n')
                            clean_emails = [e.strip() for e in vessel_emails if e.strip()]
                            all_emails.extend(clean_emails)

                            vessel_details_list.append({
                                'vessel': vessel_name,
                                'emails': clean_emails,
                                'contact': vessel_data.get('contact_details', 'N/A')
                            })

                    st.markdown("### 📋 Selected Vessels:")
                    for idx, vd in enumerate(vessel_details_list, 1):
                        with st.expander(f"{idx}. 🚢 {vd['vessel']} ({len(vd['emails'])} email(s))", expanded=False):
                            st.write("**Emails:**")
                            for email in vd['emails']:
                                st.write(f"   • {email}")
                            if vd['contact'] != 'N/A':
                                st.write(f"**Contact:** {vd['contact']}")

                    recipient_emails = '\n'.join(all_emails)

                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Vessels", len(selected_vessels))
                    with col2:
                        st.metric("Total Email Addresses", len(all_emails))

                    recipient_emails = st.text_area(
                        "Recipient Emails * (Edit if needed)",
                        value=recipient_emails,
                        height=200,
                        help="You can edit or add more emails here"
                    )
            else:
                st.warning("No vessels found in database.")

        # Email content
        st.markdown("---")
        st.subheader("📄 Email Content")
        email_subject = st.text_input("Subject", value=port_details['subject'])

        # Email format selection
        email_format = st.radio("Select Email Format:", ["HTML Template", "Custom Email (Rich Text Editor)"],
                                horizontal=True)

        # Attachments - COMMON FOR BOTH FORMATS
        st.markdown("### 📎 Attachments")

        # Show default port attachments
        st.info(f"**Default Port Attachments:** {len(port_details['attachments'])} file(s)")
        for att in port_details['attachments']:
            st.write(f"📎 {os.path.basename(att)}")

        # Additional attachments
        st.markdown("**Add More Attachments (Optional):**")
        uploaded_files = st.file_uploader(
            "Upload additional attachments",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'txt', 'zip'],
            accept_multiple_files=True,
            help="These will be added to the default port attachments",
            key="vessel_attachments"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} additional file(s) attached")
            for file in uploaded_files:
                st.write(f"📎 {file.name} ({file.size / 1024:.1f} KB)")

        if email_format == "HTML Template":
            st.markdown("### 📧 Email Preview")
            html_preview = get_html_template(port_details['portName'], port_details['country'])
            with st.expander("Click to view Email Preview", expanded=False):
                st.components.v1.html(html_preview, height=800, scrolling=True)
            email_body_html = html_preview
            email_body_plain = get_plain_text_template(port_details['portName'], port_details['country'])

        else:  # Custom Email with Rich Text Editor
            st.markdown("### ✍️ Compose Your Email")

            # Text formatting toolbar
            st.markdown("#### 🎨 Text Formatting")
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1:
                font_family = st.selectbox("Font",
                                           ["Arial", "Times New Roman", "Courier New", "Georgia", "Verdana",
                                            "Helvetica"],
                                           index=0, key="vessel_font_family")
            with col2:
                font_size = st.selectbox("Size", [10, 12, 14, 16, 18, 20, 24, 28, 32, 36], index=2,
                                         key="vessel_font_size")
            with col3:
                text_color = st.color_picker("Text Color", "#000000", key="vessel_text_color")
            with col4:
                bg_color = st.color_picker("Highlight", "#ffffff", key="vessel_bg_color")
            with col5:
                st.write("")
                st.write("")
                bold = st.checkbox("**Bold**", key="vessel_bold")
            with col6:
                st.write("")
                st.write("")
                italic = st.checkbox("*Italic*", key="vessel_italic")

            col7, col8, col9 = st.columns(3)
            with col7:
                underline = st.checkbox("Underline", key="vessel_underline")
            with col8:
                align = st.selectbox("Align", ["Left", "Center", "Right", "Justify"], key="vessel_align")
            with col9:
                line_height = st.selectbox("Line Spacing", ["1.0", "1.15", "1.5", "2.0"], index=2,
                                           key="vessel_line_height")

            # Email body editor
            st.markdown("#### 📝 Email Body")
            email_body = st.text_area(
                "Type your email message here *",
                placeholder=f"Dear Captain/Master,\n\nRegarding {port_details['portName']}, {port_details['country']}...\n\nBest regards,\nNexBay International Team",
                height=400,
                key="custom_email_body_vessel"
            )

            # Additional options
            col1, col2 = st.columns(2)
            with col1:
                add_signature = st.checkbox("Add Company Signature", value=True, key="vessel_signature")
            with col2:
                add_logo = st.checkbox("Add Company Logo", value=False, key="vessel_logo")

            # Generate HTML
            if email_body:
                style = f"font-family: {font_family}; font-size: {font_size}px; color: {text_color};"
                if bg_color != "#ffffff":
                    style += f" background-color: {bg_color};"
                if bold:
                    style += " font-weight: bold;"
                if italic:
                    style += " font-style: italic;"
                if underline:
                    style += " text-decoration: underline;"

                text_align = align.lower()
                style += f" text-align: {text_align}; line-height: {line_height};"

                formatted_body = email_body.replace('\n', '<br>')

                logo_html = ""
                if add_logo:
                    logo_html = """
                    <div style="text-align: center; margin-bottom: 20px;">
                        <h2 style="color: #0066cc; margin: 0;">⚓ NexBay International LLC</h2>
                        <p style="color: #666; font-style: italic; margin: 5px 0;">Moving Your Fleet Forward....</p>
                    </div>
                    <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
                    """

                signature = ""
                if add_signature:
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
                    """

                email_body_html = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto;">
                    {logo_html}
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

        # BCC notification
        st.info(f"ℹ️ **Note:** All emails will be BCC'd to {BCC_EMAIL}")

        # Send button
        st.markdown("---")
        if st.button("📨 Send Email", type="primary", use_container_width=True, key="send_vessel_email"):
            if recipient_emails and email_subject:
                # Check default attachments
                missing_attachments = [att for att in port_details['attachments'] if not os.path.exists(att)]

                if missing_attachments:
                    st.error("❌ Missing default attachment files:")
                    for att in missing_attachments:
                        st.write(f"- {att}")
                else:
                    # Prepare all attachments (default + uploaded)
                    all_attachments = list(port_details['attachments'])

                    if uploaded_files:
                        import tempfile
                        temp_dir = tempfile.mkdtemp()
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            all_attachments.append(file_path)

                    with st.spinner(f"Sending emails with {len(all_attachments)} attachment(s)..."):
                        success_count, failed_emails, results = email_sender.send_email_to_multiple_html(
                            recipient_emails=recipient_emails,
                            subject=email_subject,
                            port_name=port_details['portName'],
                            country=port_details['country'],
                            attachment_paths=all_attachments,
                            bcc_email=BCC_EMAIL,
                            html_body=email_body_html if email_format == "Custom Email (Rich Text Editor)" else None,
                            plain_text_body=email_body_plain if email_format == "Custom Email (Rich Text Editor)" else None
                        )

                        if success_count > 0:
                            st.success(
                                f"✅ Successfully sent {success_count} email(s) with {len(all_attachments)} attachment(s) each!")

                        if failed_emails:
                            st.error(f"❌ Failed to send to {len(failed_emails)} email(s)")
                            with st.expander("View failed emails"):
                                for email in failed_emails:
                                    st.write(f"- {email}")

                        if success_count == len(results):
                            st.balloons()

                        # Cleanup temp files
                        if uploaded_files:
                            import shutil
                            try:
                                shutil.rmtree(temp_dir)
                            except:
                                pass
            else:
                st.warning("⚠️ Please fill in all required fields!")
    else:
        st.info("👆 Please select a country and port to continue")