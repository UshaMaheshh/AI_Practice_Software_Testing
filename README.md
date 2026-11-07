# AI Practice Software Testing

An AI-assisted web application testing project built with **Python and Selenium WebDriver**. The project automates browser-based test execution, discovers web page elements, validates application functionality, and generates execution reports.

The application under test is [Practice Software Testing – Toolshop](https://practicesoftwaretesting.com/).

## Project Overview

The AI QA Automation Agent is designed to simplify web application testing by combining test planning, test case generation, Selenium-based browser automation, and test reporting.

The project performs automated checks on the Toolshop application, executes test scenarios, captures execution results, and generates HTML and JSON reports.

## Technologies Used

- **Python** – Main programming language
- **Selenium WebDriver** – Browser automation
- **Google Chrome** – Browser used for test execution
- **JSON** – Test case storage and execution results
- **HTML** – Test execution report
- **PyCharm** – Development environment
- **Git and GitHub** – Version control and project hosting

## Project Structure

```text
AI_QA_AGENT/
│
├── ai_engine/
│   ├── test_generator.py
│   └── test_planner.py
│
├── browser/
│   └── selenium_controller.py
│
├── execution/
│   ├── test_executor.py
│   └── test_runner.py
│
├── reporting/
│   └── report_generator.py
│
├── reports/
│   └── generated_test_cases.json
│
├── screenshots/
│
├── logs/
│
├── main.py
├── config.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Key Features

- Browser automation using Selenium WebDriver.
- Automated discovery of page headings, buttons, links, and input fields.
- Homepage validation.
- Product search testing.
- Invalid search testing.
- Product price sorting validation.
- Product name sorting validation.
- Product category filtering.
- Brand filtering.
- Eco-friendly product filtering.
- Login navigation validation.
- Contact page navigation validation.
- Screenshot capture.
- JSON-based test execution results.
- HTML test execution reports.

## Automated Test Scenarios

The project currently includes the following 10 automated test scenarios:

| Test ID | Test Scenario |
|---|---|
| TC001 | Verify homepage loads successfully |
| TC002 | Verify product search using a valid search term |
| TC003 | Verify invalid product search |
| TC004 | Verify price sorting (Low to High) |
| TC005 | Verify product name sorting (A to Z) |
| TC006 | Verify Hand Tools category filtering |
| TC007 | Verify ForgeFlex brand filtering |
| TC008 | Verify eco-friendly product filtering |
| TC009 | Verify Login page navigation |
| TC010 | Verify Contact page navigation |

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI_QA_AGENT.git
```

Replace `YOUR_USERNAME` with your GitHub username and use your actual repository URL.

### 2. Navigate to the project directory

```bash
cd AI_QA_AGENT
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the project

```bash
python main.py
```

Make sure Google Chrome is installed before running the Selenium tests.

## Test Execution and Reports

After execution, the project generates test results and reports in the `reports/` directory.

Expected report files include:

- `execution_results.json` – Automated test execution results.
- `qa_results.json` – Consolidated test results.
- `qa_report.html` – HTML test execution report.
- `generated_test_cases.json` – Generated test case data.

Open `qa_report.html` in a browser to review the test execution report.

Screenshots and discovery logs are also generated during execution.

## Current Test Status

The 10 automated Selenium test scenarios have successfully passed in the latest test run.

The test results are generated dynamically when the project is executed.

## Future Enhancements

- Integrate an AI/LLM-based test case generation workflow.
- Improve dynamic web element identification.
- Add more positive and negative test scenarios.
- Integrate Pytest for structured test execution.
- Add test execution logging and improved error handling.
- Integrate CI/CD using GitHub Actions.
- Add support for cross-browser testing.
- Enhance HTML reporting with execution metrics and screenshots.

## Author

Developed as a hands-on QA automation project using Python and Selenium WebDriver.

## License

This project is available for learning and demonstration purposes. Add a formal license if you intend to permit reuse or distribution.# AI_project_QA
Software testing using AI
