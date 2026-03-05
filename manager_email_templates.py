# manager_email_templates.py - Email templates for managers

def get_manager_html_template():
    """
    Generate HTML email template for managers
    """

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexBay International - Business Communication</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); padding: 40px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: bold;">
                                NEXBAY INTERNATIONAL
                            </h1>
                            <p style="color: #dbeafe; margin: 10px 0 0 0; font-size: 16px;">
                                Your Trusted Maritime Partner
                            </p>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="color: #374151; font-size: 16px; line-height: 1.8; margin: 0 0 20px 0;">
                                Dear Valued Partner,
                            </p>

                            <p style="color: #4b5563; font-size: 15px; line-height: 1.8; margin: 0 0 20px 0;">
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                            </p>

                            <p style="color: #4b5563; font-size: 15px; line-height: 1.8; margin: 0 0 20px 0;">
                                Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                            </p>

                            <!-- Highlighted Section -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left: 4px solid #2563eb; padding: 20px; border-radius: 4px;">
                                        <h3 style="color: #1e40af; margin: 0 0 10px 0; font-size: 18px;">
                                            Key Highlights
                                        </h3>
                                        <p style="color: #1e3a8a; font-size: 14px; line-height: 1.6; margin: 0;">
                                            Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <p style="color: #4b5563; font-size: 15px; line-height: 1.8; margin: 0 0 20px 0;">
                                Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.
                            </p>

                            <p style="color: #4b5563; font-size: 15px; line-height: 1.8; margin: 20px 0;">
                                We look forward to continuing our successful partnership and serving your maritime needs.
                            </p>
                        </td>
                    </tr>

                    <!-- Contact Section -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; border-top: 2px solid #e5e7eb;">
                            <h3 style="color: #1f2937; margin: 0 0 15px 0; font-size: 18px;">
                                Contact Information
                            </h3>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 5px 0;">
                                        <p style="color: #6b7280; font-size: 14px; margin: 0;">
                                            <strong style="color: #1f2937;">📧 Email:</strong><br>
                                            Info@nxbay.com | stores@nxbay.com<br>
                                            Nexbayinternational@gmail.com
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0;">
                                        <p style="color: #6b7280; font-size: 14px; margin: 0;">
                                            <strong style="color: #1f2937;">📞 Phone:</strong><br>
                                            +971569610203 (WhatsApp)
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0;">
                                        <p style="color: #6b7280; font-size: 14px; margin: 0;">
                                            <strong style="color: #1f2937;">🌐 Website:</strong><br>
                                            <a href="http://www.nxbay.com" style="color: #2563eb; text-decoration: none;">www.nxbay.com</a>
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0;">
                                        <p style="color: #6b7280; font-size: 14px; margin: 0;">
                                            <strong style="color: #1f2937;">💬 WeChat ID:</strong> Nexbayintl
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Signature -->
                    <tr>
                        <td style="padding: 30px; background-color: #ffffff;">
                            <p style="color: #374151; font-size: 14px; line-height: 1.6; margin: 0;">
                                <strong>Best regards,</strong><br>
                                <span style="color: #2563eb; font-size: 16px; font-weight: bold;">Sweety (Ms)</span><br>
                                <span style="color: #6b7280; font-size: 13px;">NEXBAY INTERNATIONAL LLC</span><br>
                                <span style="color: #6b7280; font-size: 13px;">Media city, Al messaned, Al bataeh SECTOR</span>
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); padding: 20px; text-align: center;">
                            <p style="color: #ffffff; font-size: 14px; margin: 0;">
                                © 2025 NexBay International LLC. All rights reserved.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    return html_template


def get_manager_plain_text_template():
    """
    Generate plain text email template for managers
    """

    plain_text = """Dear Valued Partner,

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

KEY HIGHLIGHTS:
Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.

We look forward to continuing our successful partnership and serving your maritime needs.

---
CONTACT INFORMATION

Email: Info@nxbay.com | stores@nxbay.com | Nexbayinternational@gmail.com
Phone: +971569610203 (WhatsApp)
Website: www.nxbay.com
WeChat ID: Nexbayintl

---
Best regards,
Sweety (Ms)
NEXBAY INTERNATIONAL LLC
Media city, Al messaned, Al bataeh SECTOR

© 2025 NexBay International LLC. All rights reserved.
"""

    return plain_text