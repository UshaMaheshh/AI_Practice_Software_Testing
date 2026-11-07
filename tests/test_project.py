def test_project_configuration():

    from config import BASE_URL

    assert BASE_URL.startswith("https://")


def test_target_website():

    from config import BASE_URL

    assert "practicesoftwaretesting.com" in BASE_URL
