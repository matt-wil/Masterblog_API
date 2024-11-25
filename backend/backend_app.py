from flask import Flask, jsonify, request
from flask_cors import CORS
from utilities import find_post_by_id, id_generator
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Temporary db
from file_handling import read_posts, save_posts

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per minute"]
)
CORS(app)  # This will enable CORS for all routes


@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    blog_posts = read_posts()

    # Handle adding a new post
    if request.method == 'POST':
        new_post = request.get_json()

        if not new_post.get('title') or not new_post.get('content'):
            return jsonify({"error": "Invalid post"}), 400

        new_post['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_post['id'] = id_generator(blog_posts)
        blog_posts.append(new_post)
        save_posts(blog_posts)

        return jsonify(new_post), 201

    # Sorting
    sort_field = request.args.get('sort', 'date')
    sort_direction = request.args.get('direction', 'asc').lower()

    if sort_field in ['date', 'title']:
        blog_posts.sort(key=lambda x: x.get(sort_field, ''), reverse=(sort_direction == 'desc'))

    # Pagination
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        if page < 1 or limit < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid page or limit"}), 400

    start = (page - 1) * limit
    end = start + limit
    paginated_posts = blog_posts[start:end]

    return jsonify(paginated_posts), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE', 'PUT'])
def manage_posts(post_id):
    blog_posts = read_posts()

    if request.method == 'DELETE':
        post = find_post_by_id(post_id, blog_posts)
        if post is None:
            return jsonify({"message": "Post not found."}), 404

        blog_posts.remove(post)
        save_posts(blog_posts)
        return jsonify({"message": "Post Deleted."}), 200

    # update route
    if request.method == 'PUT':
        post = find_post_by_id(post_id, blog_posts)
        if post is None:
            return jsonify({"message": "Post not found."}), 404

        updated_data = request.get_json()

        if 'date' in updated_data:
            try:
                datetime.strptime(updated_data['date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid date format. us YYYY-MM-DD"})

        post.update({key: value for key, value in updated_data.items() if key in ['title', 'content', 'date']})
        save_posts(blog_posts)

        return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    posts = read_posts()
    title_query = request.args.get('title', '').strip().lower()
    content_query = request.args.get('content', '').strip().lower()

    filtered_posts = [
        post for post in posts
        if (title_query.lower() in post.get('title').lower() if title_query else True)
           and
           (content_query.lower() in post.get('content').lower() if content_query else True)
    ]
    return jsonify(filtered_posts), 200


# error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error."}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
