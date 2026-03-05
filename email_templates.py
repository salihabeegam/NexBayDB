# In email_templates.py - Update the port list text dynamically

def get_html_template(port_name, country):
    """
    Generate HTML email template with styling
    """

    # Dynamic port list based on country
    if country == "OMAN":
        port_list = "Sohar, Salalah, Shinas, Duqm"
    elif country == "UAE":
        port_list = "Jebel Ali, Hamraiyah, Fujairah, Abu Dhabi Mina, Khalifa"
    elif country == "SAUDI ARABIA":
        port_list = "Jubail, Ras Al Khair, Dammam"
    else:
        port_list = "all major ports"

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexBay International - Ship Supply Services</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <!-- Main Container -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; text-align: center;">
                            <h3 style="color: #ffffff; margin: 0;font-weight: bold;">
                                Save 10% on Premium Fresh Provisions – Quality You Can Trust, Longer Expiry Guaranteed
                            </h3>
                        </td>
                    </tr>

                    <!-- Welcome Banner -->
                    <tr>
                        <td style="background-color: #dbeafe; padding: 20px; text-align: center; border-bottom: 3px solid #3b82f6;">
                            <h3 style="color: #1e40af; margin: 10px 0 0 0; font-size: 20px;">
                                Welcome to {port_name}
                            </h3>
                        </td>
                    </tr>

                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <p style="color: #1f2937; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                Dear <strong>MASTER</strong>,
                            </p>

                            <p style="color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                                We <strong>NexBay International</strong> are a dedicated service provider offering comprehensive ship supply across all <strong>{country}</strong> ports, including {port_list}.
                                We maintain a local in-stock facility to ensure fast delivery and competitive pricing.
                            </p>

                            <!-- Core Services -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                <tr>
                                    <td style="background-color: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 4px;">
                                        <h3 style="color: #1e3a8a; margin: 0 0 15px 0; font-size: 18px;">
                                            🔧 Our Core Services:
                                        </h3>
                                        <ul style="color: #374151; font-size: 14px; line-height: 1.8; margin: 0; padding-left: 20px;">
                                            <li><strong>Provisions & Bonded Stores:</strong> Guaranteed fresh items with long expiry and any damaged items must be replaced immediately.</li>
                                            <li><strong>Technical Stores:</strong> Expert sourcing of deck, engine, and cabin stores based on your exact specifications.</li>
                                            <li><strong>Ship's Spare Delivery:</strong> Rapid customs clearance and instant delivery on board.</li>
                                        </ul>
                                    </td>
                                </tr>
                            </table>

                            <!-- Exclusive Benefits -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 15px; border-radius: 4px;">
                                        <h3 style="color: #92400e; margin: 0 0 15px 0; font-size: 18px;">
                                            ⭐ Exclusive Benefits:
                                        </h3>
                                        <ul style="color: #78350f; font-size: 14px; line-height: 1.8; margin: 0; padding-left: 20px;">
                                            <li><strong>10% Flat Discount</strong> on your total order value.</li>
                                            <li><strong>Complimentary Gifts</strong> to master and crew based on order value.</li>
                                            <li><strong>Flexible Payment:</strong> Master can settle payment upon delivery.</li>
                                        </ul>
                                    </td>
                                </tr>
                            </table>

                            <p style="color: #374151; font-size: 15px; line-height: 1.6; margin: 20px 0;">
                                Please find attached updated price list and send your order list for our review.
                                Your satisfaction is our priority and we look forward to a successful long term business relationship.
                            </p>

                            <p style="color: #1e3a8a; font-size: 15px; line-height: 1.6; margin: 20px 0; font-weight: 600;">
                                Excited to show you how we combine best-in-class service with real cost-efficiency! 💼
                            </p>
                        </td>
                    </tr>

                    <!-- Contact Section -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 25px; border-top: 2px solid #e5e7eb;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td width="50%" style="vertical-align: top; padding-right: 10px;">
                                        <p style="color: #6b7280; font-size: 13px; margin: 0 0 8px 0;">
                                            <strong style="color: #1f2937;">WE CHAT ID:</strong> Nexbayintl
                                        </p>
                                        <p style="color: #6b7280; font-size: 13px; margin: 0 0 8px 0;">
                                            <strong style="color: #1f2937;">📧 Email:</strong><br>
                                            Info@nxbay.com<br>
                                            stores@nxbay.com<br>
                                            
                                        </p>
                                    </td>
                                    <td width="50%" style="vertical-align: top; padding-left: 10px;">
                                        <p style="color: #6b7280; font-size: 13px; margin: 0 0 8px 0;">
                                            <strong style="color: #1f2937;">📞 Contact:</strong><br>
                                            +971569610203 (WhatsApp)
                                        </p>
                                        <p style="color: #6b7280; font-size: 13px; margin: 0 0 8px 0;">
                                            <strong style="color: #1f2937;">🌐 Website:</strong><br>
                                            <a href="http://www.nxbay.com" style="color: #3b82f6; text-decoration: none;">www.nxbay.com</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Signature -->
                    <tr>
                        <td style="padding: 25px; background-color: #ffffff;">
                            <p style="color: #374151; font-size: 14px; line-height: 1.6; margin: 0;">
                                <strong>Thanks and best regards,</strong><br>
                                <span style="color: #1e3a8a; font-size: 16px; font-weight: bold;">Sweety (Ms)</span><br>
                                <span style="color: #6b7280; font-size: 13px;">NEXBAY INTERNATIONAL LLC</span><br>
                                <span style="color: #6b7280; font-size: 13px;">Media city, Al messaned, Al bataeh SECTOR {country}</span>
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 20px; text-align: center;">
                            <p style="color: #ffffff; font-size: 16px; font-weight: bold; margin: 0;">
                                🚢 Moving Your Fleet Forward... 🚢
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


def get_plain_text_template(port_name, country):
    """
    Generate plain text version with dynamic port list
    """

    # Dynamic port list based on country
    if country == "OMAN":
        port_list = "Sohar, Salalah, Muscat, Duqm"
    elif country == "UAE":
        port_list = "Jebel Ali, Hamriyah, Fujairah, Abu Dhabi Mina, Khalifa"
    elif country == "SAUDI ARABIA":
        port_list = "Jubail, Jeddah, Dammam"
    else:
        port_list = "all major ports"

    plain_text = f"""Dear MASTER,

HAPPY NEW YEAR & Welcome to {port_name}.

We NexBay International are a dedicated service provider offering comprehensive ship supply across all {country} ports, including {port_list}.
We maintain a local in-stock facility to ensure fast delivery and competitive pricing.

Our Core Services:
* Provisions & Bonded Stores: Guaranteed fresh items with long expiry and Any damaged items must be replaced immediately.
* Technical Stores: Expert sourcing of deck, engine, and cabin stores based on your exact specifications.
* Ship's spare delivery: Rapid customs clearance and instant delivery on board.

Exclusive Benefits:
* 10% Flat Discount on your total order value.
* Complimentary Gifts to master and crew based on order Value.
* Flexible Payment: Master can settle payment upon delivery.

Please find attached updated price list and send your order list for our review.
Your satisfaction is our priority and we look forward to a successful long term business relationship.

Excited to show you how we combines best-in-class service with real cost-efficiency

WE CHAT ID: Nexbayintl

Thanks and best regards
Sweety (Ms)
NEXBAY INTERNATIONAL LLC
Media city,
Al messaned, Al bataeh SECTOR {country}
E: Info@nxbay.com stores@nxbay.com Nexbayinternational@gmail.com
Contact number:
+971569610203 (WhatsApp)
www.nxbay.com
Moving Your Fleet Forward...
"""

    return plain_text