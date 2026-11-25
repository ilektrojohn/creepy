"""
Web App: Creepy Government Surveillance Shouldn't Be Kept Secret
Python Version: 3.9
Framework: Flask (Standard lightweight web framework)
Description: 
    An intermediate-level Flask web application that serves an educational 
    and advocacy interface highlighting global government surveillance programs, 
    techniques, civil liberties concerns, and international examples based on the 
    provided context.
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# HTML Template combining the civil-liberties advocacy content, responsive styling,
# and structured data presentation (technologies, historical examples, international programs).
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Creepy Government Surveillance Shouldn't Be Kept Secret</title>
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-color: #e0e0e0;
            --accent-color: #ff5252;
            --secondary-accent: #ff8a80;
            --border-color: #333333;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        header {
            background: linear-gradient(135deg, #2c0000, #121212);
            border-bottom: 2px solid var(--accent-color);
            padding: 3rem 1rem;
            text-align: center;
        }
        header h1 {
            margin: 0;
            font-size: clamp(2rem, 6vw, 2.5rem);
            color: var(--accent-color);
        }
        header p {
            font-style: italic;
            color: var(--secondary-accent);
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }
        .container {
            max-width: 1000px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }
        section {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        h2 {
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            color: var(--secondary-accent);
            margin-top: 0;
        }
        ul {
            padding-left: 1.5rem;
        }
        li {
            margin-bottom: 0.5rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            min-width: 480px;
        }
        .table-wrap {
            overflow-x: auto;
        }
        th, td {
            border: 1px solid var(--border-color);
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #252525;
            color: var(--accent-color);
        }
        .quote {
            background: #251212;
            border-left: 4px solid var(--accent-color);
            padding: 1rem;
            margin: 1.5rem 0;
            font-style: italic;
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: #777;
            font-size: 0.9rem;
            border-top: 1px solid var(--border-color);
        }
    </style>
</head>
<body>

    <header>
        <h1>Creepy Government Surveillance Shouldn't Be Kept Secret</h1>
        <p>A comprehensive look at civil liberties, political analysis, and global surveillance initiatives.</p>
    </header>

    <div class="container">

        <!-- Main Argument -->
        <section>
            <h2>Main Argument</h2>
            <p>The central claim is that government surveillance programs often operate with insufficient transparency and oversight, creating risks to privacy, free expression, and constitutional rights. The page argues that surveillance activities should be subject to public scrutiny, judicial review, and democratic accountability.</p>
            <div class="quote">
                The surveillance state has become a major concern in modern politics, with the potential to undermine democratic values and institutions.
            </div>
        </section>

        <!-- ACLU & EFF Position -->
        <section>
            <h2>ACLU and EFF Position</h2>
            <p>We highlight ongoing efforts by organizations like the <strong>American Civil Liberties Union (ACLU)</strong> and the <strong>Electronic Frontier Foundation (EFF)</strong> to challenge secret government surveillance. Special attention is drawn to initiatives like the Hemisphere Project—which reportedly provided law enforcement access to extensive telephone call records—advocating that defendants should be properly informed when such surveillance techniques are utilized in criminal investigations.</p>
        </section>

        <!-- Historical Context -->
        <section>
            <h2>Historical Context</h2>
            <p>Surveillance is not a modern invention; governments have tracked populations throughout history. Notable historical examples include:</p>
            <ul>
                <li><strong>Ancient Rome:</strong> Early systematic intelligence gathering.</li>
                <li><strong>Nazi Germany:</strong> Totalitarian monitoring and control grids.</li>
                <li><strong>The Soviet Union:</strong> State-wide surveillance and informant networks.</li>
                <li><strong>United States:</strong> FBI monitoring of civil-rights and anti-war activists.</li>
            </ul>
            <p>Crucially, modern technology has dramatically expanded governments' scale, speed, and analytical capacity to collect information.</p>
        </section>

        <!-- Surveillance Technologies -->
        <section>
            <h2>Surveillance Techniques & Technologies</h2>
            <p>Governments and political campaigns leverage a broad matrix of traditional and emerging intelligence gathering mechanisms:</p>
            <ul>
                <li><strong>Human Intelligence (HUMINT):</strong> The use of human sources, informants, and spies.</li>
                <li><strong>Signals Intelligence (SIGINT):</strong> The interception of communications such as phone calls and emails.</li>
                <li><strong>Open-Source Intelligence (OSINT):</strong> Collection and analysis of publicly available digital media and posts.</li>
                <li><strong>Data Mining & Predictive Analytics:</strong> Algorithms parsing massive datasets to model and predict individual behavior.</li>
                <li><strong>Facial Recognition & Biometric Monitoring:</strong> AI-powered tracking in crowds alongside DNA and fingerprint matching.</li>
                <li><strong>Online Tracking & Profiling:</strong> Cookies, metadata analysis, and voter profiling deployed during political cycles.</li>
            </ul>
        </section>

        <!-- International Examples -->
        <section>
            <h2>Global Surveillance Programs</h2>
            <p>Surveillance infrastructures span across geopolitical boundaries:</p>
            <ul>
                <li><strong>European Union:</strong> Data Retention Directive (now defunct), INDECT (automated behavioral detection), and the Schengen Information System (SIS).</li>
                <li><strong>China:</strong> Golden Shield Project, IJOP (Integrated Joint Operations Platform), and Social Credit initiatives.</li>
                <li><strong>India:</strong> Central Monitoring System (CMS), NETRA, and NATGRID.</li>
                <li><strong>Russia:</strong> SORM, CAMERTON, and the Yarovaya Law.</li>
                <li><strong>United Kingdom:</strong> Tempora, Mastering the Internet, and the National DNA Database.</li>
                <li><strong>United States:</strong> PRISM, XKeyscore, Boundless Informant, MAINWAY, MUSCULAR, and Hemisphere.</li>
            </ul>
        </section>

        <!-- Civil Liberties Concerns Table -->
        <section>
            <h2>Civil Liberties & Individual Freedoms</h2>
            <p>Unchecked surveillance inflicts severe direct and indirect consequences on democratic societies:</p>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Consequence</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Privacy</strong></td>
                            <td>Erosion of individual privacy through sweeping data collection and unconsented analysis.</td>
                        </tr>
                        <tr>
                            <td><strong>Free Speech</strong></td>
                            <td>Creation of a chilling effect on free speech and political dissent due to constant monitoring.</td>
                        </tr>
                        <tr>
                            <td><strong>Association</strong></td>
                            <td>Direct limitation on the ability of individuals and groups to freely assemble, organize, and protest.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Public Policy Questions & Conclusion -->
        <section>
            <h2>Public Policy & Conclusion</h2>
            <p>A permanent tension persists between national security, crime prevention, public safety, and individual liberties. While authorities often justify expansion as a security necessity, the absence of transparency undermines democratic accountability.</p>
            <p><strong>Conclusion:</strong> Surveillance in politics is a multifaceted issue involving complex technologies. Understanding these dynamics is essential to ensure transparency, legal oversight, and the preservation of foundational democratic values.</p>
        </section>

    </div>

    <footer>
        <p>&copy; 2026 Civil Liberties Advocacy Project. Built with Python 3.9 & Flask.</p>
    </footer>

</body>
</html>
"""

@app.route("/")
def home():
    """Renders the main advocacy and informational web page."""
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
