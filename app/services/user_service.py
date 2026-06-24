import json

USERS_FILE = "data/users.json"


def get_users():

    with open(USERS_FILE, "r") as file:
        return json.load(file)


def get_matching_users(category):

    users = get_users()

    return [
        user
        for user in users
        if user["category"] == category
    ]


def add_user(user):

    users = get_users()

    for existing_user in users:

        if (
            existing_user["email"] == user["email"]
            and
            existing_user["category"] == user["category"]
        ):
            return False

    users.append(user)

    with open(
        USERS_FILE,
        "w"
    ) as file:

        json.dump(
            users,
            file,
            indent=4
        )

    return True

def delete_user(email, category):

    users = get_users()

    updated_users = []

    for user in users:

        if not (
            user["email"] == email
            and
            user["category"] == category
        ):
            updated_users.append(user)

    with open(
        USERS_FILE,
        "w"
    ) as file:

        json.dump(
            updated_users,
            file,
            indent=4
        )
def update_user_category(email, new_category):

    users = get_users()

    for user in users:

        if user["email"] == email:

            user["category"] = new_category

            with open(
                USERS_FILE,
                "w"
            ) as file:

                json.dump(
                    users,
                    file,
                    indent=4
                )

            return True

    return False