import requests

BASE_URL = "http://localhost/policybot/api"

USERS = [
    {"email": "user1@test.com", "password": "password123", "full_name": "User One"},
    {"email": "user2@test.com", "password": "password123", "full_name": "User Two"},
]

NOTEBOOKS = [
    {"title": "User1 Notebook 1", "description": "First notebook for user 1"},
    {"title": "User1 Notebook 2", "description": "Second notebook for user 1"},
    {"title": "User2 Notebook 1", "description": "First notebook for user 2"},
    {"title": "User2 Notebook 2", "description": "Second notebook for user 2"},
]


def register_user(email: str, password: str, full_name: str) -> dict | None:
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password, "full_name": full_name},
            timeout=10,
        )
        if resp.status_code == 201:
            print(f"✓ Created user: {email}")
            return resp.json()
        elif resp.status_code == 400 and "already exists" in resp.text.lower():
            print(f"  User already exists: {email}")
            return None
        else:
            print(f"✗ Failed to create user {email}: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating user {email}: {e}")
        return None


def login_user(email: str, password: str) -> str | None:
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            print(f"✓ Logged in: {email}")
            return token
        else:
            print(f"✗ Failed to login {email}: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"✗ Error logging in {email}: {e}")
        return None


def create_notebook(token: str, title: str, description: str) -> dict | None:
    try:
        resp = requests.post(
            f"{BASE_URL}/notebooks",
            json={"title": title, "description": description},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.status_code == 201:
            data = resp.json()
            print(f"  ✓ Created notebook: {title} (id: {data.get('notebook_id')})")
            return data
        elif resp.status_code == 400 and "already exists" in resp.text.lower():
            print(f"  Notebook already exists: {title}")
            return None
        else:
            print(
                f"  ✗ Failed to create notebook {title}: {resp.status_code} - {resp.text}"
            )
            return None
    except Exception as e:
        print(f"  ✗ Error creating notebook {title}: {e}")
        return None


def list_notebooks(token: str) -> list:
    try:
        resp = requests.get(
            f"{BASE_URL}/notebooks",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("notebooks", [])
        return []
    except Exception:
        return []


def main():
    print("=" * 60)
    print("Populating test data...")
    print("=" * 60)

    user_tokens = {}
    user_notebooks = {}

    # Step 1 & 2: Register and login users
    for user in USERS:
        email = user["email"]
        print(f"\n--- Processing user: {email} ---")

        # Try to register (ignore if exists)
        register_user(email, user["password"], user["full_name"])

        # Login to get token
        token = login_user(email, user["password"])
        if token:
            user_tokens[email] = token
            # Get existing notebooks
            notebooks = list_notebooks(token)
            user_notebooks[email] = [nb["notebook_id"] for nb in notebooks]
            print(f"  Found {len(user_notebooks[email])} existing notebooks")

    # Step 3: Create notebooks for each user
    # Assign first 2 notebooks to user1, last 2 to user2
    user1_email = USERS[0]["email"]
    user2_email = USERS[1]["email"]

    print("\n--- Creating notebooks ---")

    for i, nb in enumerate(NOTEBOOKS):
        if i < 2:
            user_email = user1_email
        else:
            user_email = user2_email

        token = user_tokens.get(user_email)
        if not token:
            print(f"  ✗ No token for {user_email}, skipping {nb['title']}")
            continue

        # Check if notebook with same title already exists
        existing_ids = user_notebooks.get(user_email, [])
        existing_notebooks = list_notebooks(token)
        title_exists = any(nb["title"] == n["title"] for n in existing_notebooks)

        if title_exists:
            print(f"  Notebook already exists: {nb['title']}")
            continue

        create_notebook(token, nb["title"], nb["description"])

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for user in USERS:
        email = user["email"]
        token = user_tokens.get(email)
        if token:
            notebooks = list_notebooks(token)
            print(f"{email}: {len(notebooks)} notebooks")
            for nb in notebooks:
                print(f"  - {nb['title']} ({nb['notebook_id']})")

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
