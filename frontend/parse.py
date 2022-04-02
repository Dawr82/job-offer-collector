SOFT_SKILLS = [
    "English",
    "Polish",
    "Communication skills",
    "Problem solving",
    "Team player",
    "Proactivity",
    "Critical thinking",
    "Leadership skills",
    "Analytical skills",
    "Recruitment experience",
    "Organizational skills",
]


def get_unique_locations(data):
    unique_locations = set()
    for offer in data:
        if "locations" in offer.keys():
            unique_locations.update(offer["locations"])
    unique_locations.add("Remote")
    return list(unique_locations)


def get_unique_seniority(data):
    unique_seniority = set()
    for offer in data:
        if "seniority" in offer.keys():
            unique_seniority.update(offer["seniority"])
    unique_seniority.add("All")
    print(unique_seniority)
    return list(unique_seniority)
