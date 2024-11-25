import json
import os

file_path = os.path.join(os.path.dirname(__file__), 'blogposts.json')


def read_posts(filename=file_path):
    try:
        with open(filename, 'r') as file_obj:
            return json.load(file_obj)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_posts(posts, filename=file_path):
    try:
        with open(filename, 'w') as file_obj:
            json.dump(posts, file_obj, indent=4)
            return "Posts saved successfully"
    except Exception as e:
        return f"Something went wrong. {e}"


# posts = read_posts()
#
# print(posts)
# print(type(posts))
