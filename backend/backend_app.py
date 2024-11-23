from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


# Utility functions
def validate_post_data(data):
    if not data.get("title") or not data.get("content"):
        return False
    return True


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        new_post = request.get_json()
        if not validate_post_data(new_post):
            return jsonify({"error": "Invalid post"}), 400

        new_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_id

        POSTS.append(new_post)

    return jsonify(POSTS), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
