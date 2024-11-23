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


def find_post_by_id(post_id):
    for post in POSTS:
        if post.get('id') == post_id:
            return post
    return None


def id_generator():
    if POSTS:
        return max(post['id'] for post in POSTS) + 1
    return 1


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        new_post = request.get_json()
        if not validate_post_data(new_post):
            return jsonify({"error": "Invalid post"}), 400

        new_post['id'] = id_generator()

        POSTS.append(new_post)

    return jsonify(POSTS), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = find_post_by_id(post_id)

    if post is None:
        return jsonify({"message": f"Post with id {post_id} not found"}), 404

    POSTS.remove(post)

    return jsonify({"message": f"Post with id {post_id} has been successfully deleted"}), 200


# error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
