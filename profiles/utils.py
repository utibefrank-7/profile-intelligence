import requests


GENDERIZE_URL = "https://api.genderize.io"
AGIFY_URL = "https://api.agify.io"
NATIONALIZE_URL = "https://api.nationalize.io"


class UpstreamValidationError(Exception):
    def __init__(self, api_name: str):
        self.api_name = api_name
        super().__init__(f"{api_name} returned an invalid response")


def normalize_name(name: str) -> str:
    # WHY: Storing names consistently (lowercase, stripped) prevents
    # "John" and "john" being treated as different profiles.
    return name.strip().lower()


def classify_age_group(age: int) -> str:
    # WHY: This function must never receive None — the caller in views.py
    # guards against that. But we keep the ranges explicit and exhaustive.
    if 0 <= age <= 12:
        return "child"
    if 13 <= age <= 19:
        return "teenager"
    if 20 <= age <= 59:
        return "adult"
    return "senior"


def fetch_genderize(name: str) -> dict:
    response = requests.get(GENDERIZE_URL, params={"name": name}, timeout=15)
    response.raise_for_status()
    data = response.json()

    # WHY: Genderize returns {"gender": null, "count": 0} for unknown names.
    # We treat that as an upstream validation failure (502), not our bug.
    if data.get("gender") is None or data.get("count") == 0:
        raise UpstreamValidationError("Genderize")

    return data


def fetch_agify(name: str) -> dict:
    response = requests.get(AGIFY_URL, params={"name": name}, timeout=15)
    response.raise_for_status()
    data = response.json()

    # WHY: Agify returns {"age": null} for names it doesn't know.
    if data.get("age") is None:
        raise UpstreamValidationError("Agify")

    return data


def fetch_nationalize(name: str) -> dict:
    response = requests.get(NATIONALIZE_URL, params={"name": name}, timeout=15)
    response.raise_for_status()
    data = response.json()

    countries = data.get("country") or []
    if not countries:
        raise UpstreamValidationError("Nationalize")

    return data


def get_top_country(nationalize_data: dict) -> tuple[str, float]:
    countries = nationalize_data.get("country", [])
    # WHY: max() by probability picks the most likely nationality.
    top_country = max(countries, key=lambda item: item["probability"])
    return top_country["country_id"], top_country["probability"]