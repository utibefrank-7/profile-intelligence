import requests

GENDERIZE_URL = "https://api.genderize.io"
AGIFY_URL = "https://api.agify.io"
NATIONALIZE_URL = "https://api.nationalize.io"


def get_gender(name):
    response = requests.get(GENDERIZE_URL, params={"name": name})
    data = response.json()

    if not data.get("gender") or data.get("count", 0) == 0:
        raise ValueError("Genderize returned an invalid response")

    return {
        "gender": data["gender"],
        "gender_probability": data["probability"],  # renamed to match model
        "sample_size": data["count"],               # renamed to match model
    }


def get_age(name):
    response = requests.get(AGIFY_URL, params={"name": name})  # fixed: requests not request
    data = response.json()

    if data.get("age") is None:  # fixed: "age" as string not variable
        raise ValueError("Agify returned an invalid response")

    age = data["age"]  # now safe to assign after the check

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
    response = requests.get(NATIONALIZE_URL, params={"name": name})  # fixed typo
    data = response.json()

    countries = data.get("country", [])  # fixed: consistent variable name

    if not countries:
        raise ValueError("Nationalize returned an invalid response")

    top_country = max(countries, key=lambda c: c["probability"])  # fixed: countries not country

    return {
        "country_id": top_country["country_id"],        # matches model field
        "country_probability": top_country["probability"],  # matches model field
    }


def intelligent_profile(name):
    gender_data = get_gender(name)
    age_data = get_age(name)
    nationality_data = get_nationality(name)

    return {**gender_data, **age_data, **nationality_data}