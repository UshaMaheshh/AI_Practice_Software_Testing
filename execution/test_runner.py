from datetime import datetime


def run_basic_checks(discovery):

    results = []

    results.append({
        "test": "Homepage title exists",
        "status": "PASS" if discovery.get("title") else "FAIL",
        "details": discovery.get("title", "Missing title")
    })

    results.append({
        "test": "Homepage headings discovered",
        "status": "PASS" if discovery.get("elements", {}).get(
            "headings"
        ) else "FAIL",
        "details": "Heading discovery completed"
    })

    results.append({
        "test": "Website navigation discovered",
        "status": "PASS" if discovery.get("elements", {}).get(
            "links"
        ) else "FAIL",
        "details": "Link discovery completed"
    })

    return {
        "execution_time": datetime.now().isoformat(),
        "results": results
    }
