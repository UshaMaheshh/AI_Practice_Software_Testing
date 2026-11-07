
import json
from html import escape
from datetime import datetime

from config import REPORT_DIR


def generate_report(discovery, execution):
    """
    Generate JSON and HTML QA reports.

    Compatible with the execution results returned by
    execution/test_executor.py.
    """

    # --------------------------------------------------------
    # CREATE REPORT DIRECTORY
    # --------------------------------------------------------

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "qa_results.json"
    html_path = REPORT_DIR / "qa_report.html"

    # --------------------------------------------------------
    # GET DISCOVERY INFORMATION
    # --------------------------------------------------------

    website_url = (
        discovery.get("url")
        or discovery.get("website")
        or discovery.get("target_url")
        or "Not available"
    )

    page_title = (
        discovery.get("title")
        or discovery.get("page_title")
        or "Not available"
    )

    # --------------------------------------------------------
    # GET EXECUTION RESULTS
    # --------------------------------------------------------

    results = execution.get("results", [])

    passed = sum(
        1 for test in results
        if str(test.get("status", "")).upper() == "PASS"
    )

    failed = sum(
        1 for test in results
        if str(test.get("status", "")).upper() == "FAIL"
    )

    not_executed = sum(
        1 for test in results
        if str(test.get("status", "")).upper()
        in ("NOT_EXECUTED", "NOT EXECUTED")
    )

    total = execution.get("total", len(results))

    execution_time = (
        execution.get("execution_time")
        or execution.get("duration")
        or "Not available"
    )

    # --------------------------------------------------------
    # SAVE JSON REPORT
    # --------------------------------------------------------

    report_data = {
        "website": website_url,
        "page_title": page_title,
        "report_generated": datetime.now().isoformat(),
        "execution_summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "not_executed": not_executed,
            "execution_time": execution_time
        },
        "discovery": discovery,
        "execution": execution
    }

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(
            report_data,
            file,
            indent=4,
            default=str
        )

    # --------------------------------------------------------
    # GENERATE HTML TEST RESULT ROWS
    # --------------------------------------------------------

    rows = ""

    for test in results:

        test_id = str(
            test.get("id")
            or test.get("test_id")
            or ""
        )

        test_name = str(
            test.get("name")
            or test.get("test")
            or test_id
            or "Unnamed test"
        )

        status = str(
            test.get("status", "UNKNOWN")
        ).upper()

        details = str(
            test.get("message")
            or test.get("details")
            or "No additional details"
        )

        screenshot = test.get("screenshot")

        if screenshot:
            screenshot_html = (
                f'<a href="{escape(str(screenshot), quote=True)}" '
                f'target="_blank">View screenshot</a>'
            )
        else:
            screenshot_html = "Not available"

        if status == "PASS":
            status_class = "pass"
        elif status == "FAIL":
            status_class = "fail"
        else:
            status_class = "not-executed"

        rows += f"""
        <tr>
            <td>{escape(test_id)}</td>
            <td>{escape(test_name)}</td>
            <td class="{status_class}">{escape(status)}</td>
            <td>{escape(details)}</td>
            <td>{screenshot_html}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5">No test results available.</td>
        </tr>
        """

    # --------------------------------------------------------
    # GENERATE HTML REPORT
    # --------------------------------------------------------

    html = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>AI QA Testing Report</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f6fa;
                color: #333;
            }}

            h1 {{
                color: #263859;
            }}

            h2 {{
                color: #263859;
                margin-top: 30px;
            }}

            .summary {{
                padding: 25px;
                background: white;
                margin-bottom: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}

            .summary p {{
                font-size: 16px;
            }}

            .statistics {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 20px;
            }}

            .stat-card {{
                background: white;
                padding: 18px;
                border-radius: 8px;
                min-width: 120px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}

            .stat-card h3 {{
                margin: 0 0 10px 0;
                color: #555;
                font-size: 14px;
            }}

            .stat-card p {{
                font-size: 25px;
                font-weight: bold;
                margin: 0;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                margin-top: 15px;
            }}

            th, td {{
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #263859;
                color: white;
            }}

            tr:nth-child(even) {{
                background: #f8f9fc;
            }}

            .pass {{
                color: #16803c;
                font-weight: bold;
            }}

            .fail {{
                color: #d62828;
                font-weight: bold;
            }}

            .not-executed {{
                color: #b7791f;
                font-weight: bold;
            }}

            a {{
                color: #2457a7;
            }}

            footer {{
                margin-top: 30px;
                color: #777;
                font-size: 13px;
            }}

        </style>

    </head>

    <body>

        <h1>Autonomous AI QA Testing Report</h1>

        <div class="summary">

            <h2>Website Information</h2>

            <p>
                <strong>Website:</strong>
                {escape(str(website_url))}
            </p>

            <p>
                <strong>Page Title:</strong>
                {escape(str(page_title))}
            </p>

            <p>
                <strong>Report Generated:</strong>
                {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>

            <p>
                <strong>Execution Time:</strong>
                {escape(str(execution_time))}
            </p>

        </div>

        <h2>Test Execution Summary</h2>

        <div class="statistics">

            <div class="stat-card">
                <h3>Total Tests</h3>
                <p>{total}</p>
            </div>

            <div class="stat-card">
                <h3>Passed</h3>
                <p class="pass">{passed}</p>
            </div>

            <div class="stat-card">
                <h3>Failed</h3>
                <p class="fail">{failed}</p>
            </div>

            <div class="stat-card">
                <h3>Not Executed</h3>
                <p class="not-executed">{not_executed}</p>
            </div>

        </div>

        <h2>Detailed Test Results</h2>

        <table>

            <thead>
                <tr>
                    <th>Test ID</th>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Details</th>
                    <th>Screenshot</th>
                </tr>
            </thead>

            <tbody>
                {rows}
            </tbody>

        </table>

        <footer>
            Generated by Autonomous AI QA Testing Agent.
        </footer>

    </body>

    </html>
    """

    # --------------------------------------------------------
    # SAVE HTML REPORT
    # --------------------------------------------------------

    html_path.write_text(
        html,
        encoding="utf-8"
    )

    print("\nQA reports generated successfully!")
    print("HTML report:", html_path)
    print("JSON report:", json_path)

    return html_path
