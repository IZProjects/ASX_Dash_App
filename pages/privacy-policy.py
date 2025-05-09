import dash
from dash import html, dcc
import dash_mantine_components as dmc

dash.register_page(__name__, name='privacy-policy') # '/' is home page



layout = dmc.Box([
    dmc.Title(f"Privacy Policy", order=1, style={'margin-bottom': '10px'}),
    dmc.Text("Effective April 13th 2025"),
    dmc.Text("Butterfly Technologies Pty Ltd (“Butterfly Technologies”, “we”, “our”, or “us”) is committed to safeguarding your privacy. This Privacy Policy outlines how we collect, use, store, and disclose your personal information when you interact with our website and services. By accessing or using our website, you agree to the terms set out in this Policy. Contact us at info@tickersight.com.au for any queries.", style={'margin-bottom': '20px'}),

    dmc.Title(f"1. Overview", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Butterfly Technologies does not collect personally identifiable information unless it is voluntarily submitted by you. This may occur when you create an account, contact us, subscribe to communications, interact on social media, or engage with other features of the site.\nWe are committed to handling your personal data responsibly and in accordance with the Privacy Act 1988 and the Australian Privacy Principles (APPs)."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"2. Collection of Personal Information", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("You may provide personal information such as your name, email address, and contact details when: creating an account, subscribing to email updates, sending enquiries or feedback, commenting on content or interacting with our social channels. This information is collected solely for the purpose of delivering our services, improving user experience, and corresponding with you. We do not sell, rent, or share your personal information with unauthorised third parties."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"3. Communications and Unsubscribing", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "You may receive occasional communications from us, including newsletters, updates, and service-related notifications. All marketing-related emails include an unsubscribe link. Operational communications (e.g. password resets) may not include this option. You can opt out of marketing communications at any time by clicking 'Unsubscribe' in the email or contacting us directly."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"4. Use of Personal Information", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "We collect and use personal information to: provide access to our website’s features, deliver subscription services, personalise your experience (e.g. saving preferences, watchlists), respond to enquiries and requests, comply with legal obligations.\nYour information is accessible only to Butterfly Technologies, its related entities, and a limited number of authorised third-party service providers (e.g. email platforms, payment processors), who are required to maintain the confidentiality of your information and use it only for the specified purposes.\nIf Butterfly Technologies or any of its related businesses is sold or merged, your data may be transferred to the acquiring entity. In such an event, your personal information will remain subject to the commitments outlined in this Privacy Policy."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"5. Subscription and Payment Information", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "When you subscribe to a paid service, we may collect additional data such as your billing address, country, postcode, and payment method details (e.g. via Stripe). This information is used exclusively for payment processing and is not shared or used for marketing. You may request deletion of this information at any time via our Contact page."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"6. Anonymous Usage Data", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "We automatically collect non-personally identifiable information such as: browser type and version, operating system, IP address, pages visited, access times, referring websites. This data is used internally for analytical purposes, service improvement, and site administration."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"7. Website Analytics", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "We use third-party analytics services such as Google Analytics to monitor website performance and user engagement. These tools collect anonymised data using cookies, which help us understand site traffic and improve the user experience. This data does not personally identify you unless you have voluntarily provided identifying information (e.g. by creating an account)."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"8. Advertising and Cookies", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "We may partner with advertising platforms (such as Google AdSense) to deliver contextual or interest-based advertising. These platforms use cookies and similar technologies to display more relevant ads to visitors based on their browsing behaviour. You can disable cookies in your browser settings, though this may limit the functionality of the website and certain personalised features."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"9. External Links", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "Our website may contain links to third-party sites. These external websites operate independently and are governed by their own privacy policies. We are not responsible for the content or privacy practices of external websites."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"10. Access and Correction of Personal Information", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "You may request access to, or correction of, your personal information at any time. We may require you to verify your identity before processing such requests for security purposes. Requests can be made through our Contact page."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"11. Deleting Your Personal Information", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "You have the right to request deletion of your personal information from our systems. Such requests can be made at any time through our Contact page. We will action your request as soon as reasonably practicable, unless we are required to retain the information for legal or operational reasons."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"12. Updates to This Policy", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "We reserve the right to amend this Privacy Policy at any time. Changes will take effect immediately upon being published on our website. We recommend you periodically review this page to stay informed about how we protect your personal data.\nContinued use of the site or services after any changes have been made constitutes your acceptance of the updated terms."),

    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '50px', 'margin-bottom': '20px'}),
    dmc.Group([dcc.Markdown(f'[Terms and Conditions](/toc)'), dcc.Markdown(f'[Privacy Policy](/privacy-policy)')],
              gap='md', justify='flex-end'),

], style={'margin-left': '20px', 'margin-right': '20px'})
