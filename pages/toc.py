import dash
from dash import html, dcc
import dash_mantine_components as dmc

dash.register_page(__name__, name='toc') # '/' is home page



layout = dmc.Box([
    dmc.Title(f"Terms and Conditions", order=1, style={'margin-bottom': '10px'}),
    dmc.Text("Effective April 13th 2025"),
    dmc.Text("Please read the following terms and conditions carefully. By accessing or using this website, you confirm that you have read, understood, and agree to be bound by these Terms of Use.", style={'margin-bottom': '20px'}),

    dmc.Title(f"1. About Butterfly Technologies", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Butterfly Technologies Pty Ltd (“Butterfly Technologies”, “we”, “our”, or “us”) operates this website to provide general information, commentary, and data related to financial markets. Butterfly Technologies is not a financial institution or a licensed provider of financial advice. We are an information provider and content publisher only. Contact us at info@tickersight.com.au for any queries."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"2. General Information Only", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("All content published on the Butterfly Technologies website is provided for general informational purposes. It does not constitute financial product advice, nor should it be relied upon when making financial or investment decisions."),
    dmc.Text("We do not consider your specific financial objectives, circumstances, or needs. Before acting on any information, you should seek advice from a licensed financial adviser or other qualified professional."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"3. No Financial Advice or Recommendations", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Nothing on this website is intended to imply a recommendation, opinion, or endorsement of any specific financial product, asset class, or investment strategy. Butterfly Technologies does not provide personalised investment advice, and you should not interpret any material on our platform as such."),
    dmc.Text("Investing involves risk. You are solely responsible for evaluating the merits and risks associated with the use of any information provided by Butterfly Technologies."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"4. Subscription Services", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Butterfly Technologies offers premium subscription services that provide access to additional market content. These services are intended to offer general insights and commentary only, and do not constitute personalised financial advice."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"5. Accuracy and Reliability of Information", order=4, style={'margin-bottom': '10px'}),
    dmc.Text(
        "We take reasonable steps to ensure the information on our website is accurate, current, and complete. However, we do not guarantee the reliability, timeliness, or suitability of any content. Market data and other information may be sourced from third parties, and we cannot guarantee its accuracy or completeness. All information is subject to change without notice."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"6. Intellectual Property", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("All intellectual property on this website—including content, graphics, logos, and layout—is owned by or licensed to Butterfly Technologies and is protected under applicable copyright, trademark, and intellectual property laws."),
    dmc.Text("You may not reproduce, modify, republish, distribute, or commercially exploit any content from the site without prior written permission, except as permitted under applicable laws (e.g., fair dealing for personal use)."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"7. Prohibited Use", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("You must not use any automated system (including bots, scrapers, or scripts) to access, extract, or copy content or data from this website. Butterfly Technologies reserves the right to restrict or revoke access if such activity is detected."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"8. Confidentiality of Paid Content", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Materials provided as part of paid services are confidential and for the subscriber’s personal use only. Republishing, sharing, or redistributing this content in any form is strictly prohibited."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"9. Third-Party Content and Advertising", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Our website may display advertisements or include links to third-party websites. Butterfly Technologies does not endorse or guarantee the accuracy, legality, or content of third-party materials. Any engagement with third-party content is at your own risk and subject to their terms and privacy policies."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"10. Modifications to Terms and Services", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Butterfly Technologies reserves the right to update these Terms of Use at any time without prior notice. Continued use of the website after changes are published constitutes acceptance of the revised terms. We may also modify or discontinue website features or services at our sole discretion."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"11. Risk and Performance Disclaimer", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("Past performance is not a reliable indicator of future results. Simulated or back-tested results do not reflect actual trading conditions and may not account for factors such as liquidity, fees, or slippage."),
    dmc.Text("Investment decisions carry inherent risks, including the potential loss of capital. Users should exercise independent judgment and seek professional advice where appropriate."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"12. Limitation of Liability", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("To the fullest extent permitted by law, Butterfly Technologies and its affiliates, directors, employees, and licensors disclaim all liability for any direct, indirect, incidental, special, or consequential loss or damage, including but not limited to loss of profits, revenue, data, or business interruption, arising from your use of (or inability to use) our website or services."),
    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '20px', 'margin-bottom': '20px'}),

    dmc.Title(f"13. Jurisdiction and Governing Law", order=4, style={'margin-bottom': '10px'}),
    dmc.Text("These Terms are governed by the laws of New South Wales Australia, Australia. You irrevocably submit to the exclusive jurisdiction of the courts of New South Wale Australia for any proceedings arising out of or in connection with these Terms.", style={'margin-bottom': '20px'}),

    dmc.Container(html.Hr(), fluid=True, style={'margin-top': '50px', 'margin-bottom': '20px'}),
    dmc.Group([dcc.Markdown(f'[Terms and Conditions](/toc)'), dcc.Markdown(f'[Privacy Policy](/privacy-policy)')],
              gap='md', justify='flex-end'),

], style={'margin-left': '20px', 'margin-right': '20px'})
