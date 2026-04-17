import requests

GENDERIZE_URL = "https://api.genderize.io"
AGIFY_URL = "https://api.agify.io"
NATIONALIZE_URL = "https://api.nationalize.io"


def get_gender(name):
    response = requests.get(GENDERIZE_URL, params={"name": name}, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("gender") or data.get("count", 0) == 0:
        raise ValueError("Genderize returned an invalid response")

    return {
        "gender": data["gender"],
        "gender_probability": data["probability"],
        "sample_size": data["count"],
    }


def get_age(name):
    response = requests.get(AGIFY_URL, params={"name": name}, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("age") is None:
        raise ValueError("Agify returned an invalid response")

    age = data["age"]

    if age <= 12:
        age_group = "child"
    elif age <= 19:
        age_group = "teenager"
    elif age <= 59:
        age_group = "adult"
    else:
        age_group = "senior"

    return {
        "age": age,
        "age_group": age_group,
    }


def get_nationality(name):
    response = requests.get(NATIONALIZE_URL, params={"name": name}, timeout=10)
    response.raise_for_status()
    data = response.json()

    countries = data.get("country", [])

    if not countries:
        raise ValueError("Nationalize returned an invalid response")

    top_country = max(countries, key=lambda c: c["probability"])

    return {
        "country_id": top_country["country_id"],
        "country_probability": top_country["probability"],
    }


def intelligent_profile(name):
    gender_data = get_gender(name)
    age_data = get_age(name)
    nationality_data = get_nationality(name)

    return {**gender_data, **age_data, **nationality_data}