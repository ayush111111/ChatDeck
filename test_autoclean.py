import json


def test_function():
    # Only using json, not the other imports
    data = {"test": "value"}
    return json.dumps(data)


if __name__ == "__main__":
    result = test_function()
    print(result)
