from pathlib import Path

import markdown


def render_pdf_from_markdown(
    markdown_text: str,
    output_path: Path,
) -> Path:
    """
    Convert a Markdown report to a PDF file.
    """

    html_body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code"],
    )

    html = f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.5;
                color: #222;
            }}
            h1, h2, h3 {{
                color: #111;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 12px;
                margin-bottom: 24px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #f3f3f3;
            }}
            code {{
                background: #f5f5f5;
                padding: 2px 4px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from weasyprint import HTML
    except OSError as exc:
        raise RuntimeError(
            "PDF rendering requires WeasyPrint native dependencies on Windows."
        ) from exc

    HTML(string=html).write_pdf(str(output_path))

    return output_path
