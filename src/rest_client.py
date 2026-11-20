"""Read user data from the JSONPlaceholder public REST API."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE_URL = "https://jsonplaceholder.typicode.com"


def get_json(path: str, timeout: int = 10) -> Any:
    """Send a GET request and decode the JSON response."""
    url = f"{API_BASE_URL}{path}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "http-rest-practice/1.0",
        },
        method="GET",
    )

    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"API returned unexpected status: {response.status}")
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def show_user(user: dict[str, Any]) -> None:
    """Print the fields used in this practical assignment."""
    address = user.get("address") or {}
    company = user.get("company") or {}
    print(f"ID:       {user.get('id', '—')}")
    print(f"Name:     {user.get('name', '—')}")
    print(f"Username: {user.get('username', '—')}")
    print(f"Email:    {user.get('email', '—')}")
    print(f"City:     {address.get('city', '—')}")
    print(f"Company:  {company.get('name', '—')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Get users from JSONPlaceholder.")
    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="ID of a user to display (default: 1)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Display all users instead of one user",
    )
    args = parser.parse_args()

    if args.user_id < 1:
        parser.error("--user-id must be a positive integer")

    path = "/users" if args.all else f"/users/{args.user_id}"
    try:
        result = get_json(path)
        if args.all:
            if not isinstance(result, list):
                raise ValueError("Expected a JSON array from the API")
            for index, user in enumerate(result):
                if not isinstance(user, dict):
                    continue
                if index:
                    print("\n" + "-" * 40)
                show_user(user)
        else:
            if not isinstance(result, dict) or not result:
                print(f"User with ID {args.user_id} was not found.")
                return 1
            show_user(result)
        return 0
    except HTTPError as error:
        print(f"HTTP error: {error.code} {error.reason}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as error:
        print(f"Network error: {error}", file=sys.stderr)
        return 1
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RuntimeError) as error:
        print(f"Response error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
