# pages/invoice_operations.py
import streamlit as st
import pandas as pd
from io import BytesIO


def show_invoice_page(db):
    """Invoice page with tabs"""

    tab = st.radio("", ["📝 Generate Invoice", "📋 View Invoices"],
                   horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if tab == "📝 Generate Invoice":
        show_generate_invoice(db)
    elif tab == "📋 View Invoices":
        show_view_invoices(db)


def show_generate_invoice(db):
    """Generate invoice"""
    st.subheader("📄 Generate Invoice & Delivery Note")

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

    # Invoice details
    col1, col2 = st.columns(2)

    with col1:
        invoice_number = st.text_input("Invoice Number *", value=suggested_invoice)
        vessel_name = st.text_input("Vessel Name *", placeholder="Enter vessel name")
        invoice_type = st.selectbox("Invoice Type *",
                                    ["PVT provision", "Ship provision", "Bonded Stores", "Technical Stores"])

    with col2:
        port_of_delivery = st.text_input("Port of Delivery *", placeholder="e.g., Fujairah Port")
        currency = st.radio("Currency *", ["USD", "AED"], horizontal=True)
        output_format = st.multiselect("Output Format *", ["PDF", "Word"], default=["PDF", "Word"])

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

    # Template
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

                if st.button("🚀 Generate Invoice & Delivery Note", type="primary", use_container_width=True):
                    if invoice_number and vessel_name and port_of_delivery:
                        with st.spinner("Generating documents..."):
                            from invoice_generator import generate_combined_word, generate_combined_pdf

                            invoice_data = {
                                'invoice_number': invoice_number,
                                'vessel_name': vessel_name,
                                'port_of_delivery': port_of_delivery,
                                'invoice_type': invoice_type,
                                'currency': currency
                            }

                            generated_files = []

                            try:
                                if "Word" in output_format:
                                    combined_word, total = generate_combined_word(df.copy(), invoice_data)
                                    generated_files.append(('combined_word', combined_word, total))

                                if "PDF" in output_format:
                                    combined_pdf, total = generate_combined_pdf(df.copy(), invoice_data)
                                    generated_files.append(('combined_pdf', combined_pdf, total))

                                success, msg = db.insert_invoice(
                                    invoice_number, vessel_name, port_of_delivery,
                                    invoice_type, currency, generated_files[0][2]
                                )

                                if success:
                                    st.success("✅ Documents generated!")
                                else:
                                    st.warning(f"⚠️ Generated but save failed: {msg}")

                                st.subheader("📥 Download Generated Documents")

                                col1, col2 = st.columns(2)

                                for file_type, file_data, _ in generated_files:
                                    if file_type == 'combined_word':
                                        with col1:
                                            st.download_button(
                                                label="📄 Download Word",
                                                data=file_data,
                                                file_name=f"Invoice_DN_{invoice_number}.docx",
                                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                use_container_width=True
                                            )
                                    elif file_type == 'combined_pdf':
                                        with col2:
                                            st.download_button(
                                                label="📕 Download PDF",
                                                data=file_data,
                                                file_name=f"Invoice_DN_{invoice_number}.pdf",
                                                mime="application/pdf",
                                                use_container_width=True
                                            )

                                st.balloons()

                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Fill all required fields!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def show_view_invoices(db):
    """View all invoices"""
    st.subheader("📋 All Invoices")
    invoices = db.get_all_invoices()

    if invoices:
        df = pd.DataFrame(invoices)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No invoices found")