
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DISCOVERY_FILE = BASE_DIR / "logs" / "discovery.json"

OUTPUT_FILE = BASE_DIR / "reports" / "generated_test_cases.json"


def generate_test_cases():

    print("\n====================================")
    print("     AUTOMATIC TEST CASE GENERATOR")
    print("====================================")

    if not DISCOVERY_FILE.exists():
        raise FileNotFoundError(
            "Discovery file not found. Run main.py first."
        )

    with open(
        DISCOVERY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        discovery = json.load(file)

    page_content = discovery.get(
        "page_content", ""
    ).lower()

    elements = discovery.get(
        "elements", {}
    )

    test_cases = []

    def add_test(
        test_id,
        name,
        feature,
        priority,
        steps,
        expected
    ):

        test_cases.append({
            "id": test_id,
            "name": name,
            "feature": feature,
            "priority": priority,
            "steps": steps,
            "expected_result": expected,
            "status": "NOT_EXECUTED"
        })

    # Homepage tests

    add_test(
        "TC001",
        "Verify homepage loads",
        "Homepage",
        "High",
        ["Open the website"],
        "Homepage should load successfully"
    )

    # Search tests

    if "search" in page_content:

        add_test(
            "TC002",
            "Search for an existing product",
            "Search",
            "High",
            [
                "Locate the search input",
                "Enter a known product name",
                "Submit the search"
            ],
            "Matching products should be displayed"
        )

        add_test(
            "TC003",
            "Search for a nonexistent product",
            "Search",
            "Medium",
            [
                "Enter a nonexistent product name",
                "Submit the search"
            ],
            "No matching products should be displayed"
        )

    # Sorting tests

    if "price (low - high)" in page_content:

        add_test(
            "TC004",
            "Sort products by lowest price",
            "Sorting",
            "High",
            [
                "Select Price (Low - High)",
                "Inspect displayed product prices"
            ],
            "Products should be ordered by ascending price"
        )

    if "name (a - z)" in page_content:

        add_test(
            "TC005",
            "Sort products alphabetically",
            "Sorting",
            "Medium",
            [
                "Select Name (A - Z)",
                "Inspect product names"
            ],
            "Products should be ordered alphabetically"
        )

    # Category tests

    if "hand tools" in page_content:

        add_test(
            "TC006",
            "Filter products by Hand Tools",
            "Category",
            "High",
            [
                "Select Hand Tools category",
                "Inspect displayed products"
            ],
            "Only matching category products should appear"
        )

    # Brand tests

    if "forgeflex tools" in page_content:

        add_test(
            "TC007",
            "Filter products by brand",
            "Brand",
            "Medium",
            [
                "Select ForgeFlex Tools",
                "Inspect displayed products"
            ],
            "Products from the selected brand should appear"
        )

    # Eco-friendly filter

    if "eco-friendly products" in page_content:

        add_test(
            "TC008",
            "Filter eco-friendly products",
            "Sustainability",
            "Medium",
            [
                "Enable eco-friendly products filter",
                "Inspect displayed products"
            ],
            "Only eligible eco-friendly products should appear"
        )

    # Login navigation

    login_links = [
        link for link in elements.get("links", [])
        if "sign in" in link.get("text", "").lower()
    ]

    if login_links:

        add_test(
            "TC009",
            "Verify login page navigation",
            "Authentication",
            "High",
            [
                "Click Sign in",
                "Verify login page"
            ],
            "Login page should be displayed"
        )

    # Contact navigation

    contact_links = [
        link for link in elements.get("links", [])
        if "contact" in link.get("text", "").lower()
    ]

    if contact_links:

        add_test(
            "TC010",
            "Verify contact page navigation",
            "Contact",
            "Medium",
            [
                "Click Contact",
                "Verify contact page"
            ],
            "Contact page should be displayed"
        )

    result = {
        "website": discovery.get("url"),
        "page_title": discovery.get("title"),
        "total_test_cases": len(test_cases),
        "test_cases": test_cases
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print("\nGenerated test cases:")

    for test in test_cases:

        print(
            test["id"],
            "-",
            test["name"],
            "-",
            test["priority"]
        )

    print("\nTotal test cases:", len(test_cases))

    print("\nSaved:", OUTPUT_FILE)

    return result


if __name__ == "__main__":

    generate_test_cases()
