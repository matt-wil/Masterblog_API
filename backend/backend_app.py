from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from utilities import find_post_by_id, id_generator
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint

# Temporary db
from file_handling import read_posts, save_posts

app = Flask(__name__, static_folder='static')
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per minute"]
)
CORS(app)  # This will enable CORS for all routes


@app.route('/api/v1/posts', methods=['GET', 'POST'])
def posts_v1():
    """
    Handle GET and POST requests for posts.

    GET /api/v1/posts
    Returns a list of posts, which can be sorted by title or content in ascending or descending order.
    The list can be paginated by specifying the page and limit query parameters.

    POST /api/v1/posts
    Adds a new post. The post must have a title and content. Returns the newly added post with a 201 status code.

    Error Codes:
        400: Invalid post, invalid sort field, invalid sort direction, invalid page, or invalid limit.
        404: Post not found.
    """
    blog_posts = read_posts()

    # Handle adding a new post
    if request.method == 'POST':
        new_post = request.get_json()

        if not new_post.get('title') or not new_post.get('content'):
            return jsonify({"error": "Invalid post"}), 400

        new_post['likes'] = 0
        new_post['dislikes'] = 0
        new_post['comments'] = []
        new_post['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_post['id'] = id_generator(blog_posts)
        blog_posts.append(new_post)
        save_posts(blog_posts)

        return jsonify(new_post), 201

    # Sorting
    valid_sort_fields = ['title', 'content']
    valid_sort_direction = ['asc', 'desc']
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc').lower()

    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({"error": f"Invalid sort field... Must be one of {valid_sort_fields}"})
    if sort_direction and sort_direction not in valid_sort_direction:
        return jsonify({"error": f"Invalid sort field... Must be one of {valid_sort_direction}"})
    if sort_field:
        blog_posts.sort(key=lambda x: x.get(sort_field, ''),
                        reverse=(sort_direction == 'desc'))

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


@app.route('/api/v1/posts/<int:post_id>', methods=['DELETE', 'PUT'])
def manage_posts_v1(post_id):
    """
    DELETE /api/v1/posts/<int:post_id>
    Deletes a post given the ID. Returns a 404 if the post is not found, or a 200 if the post is deleted.

    PUT /api/v1/posts/<int:post_id>
    Updates a post given the ID. Returns a 404 if the post is not found, or a 200 if the post is updated.
    The fields that can be updated are title and content.
    """
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

        post['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        allowed_fields = ['title', 'content']
        for key, value in updated_data.items():
            if key in allowed_fields:
                post[key] = value

        save_posts(blog_posts)

        return jsonify(post), 200


@app.route('/api/v1/posts/search', methods=['GET'])
def search_post_v1():
    """
    GET /api/v1/posts/search
    Returns a list of posts that match a given title or content query.

    Returns:
        A list of posts that match the given title and content query.

    Example:
        GET /api/v1/posts/search?title=hello&content=world
        Returns a list of posts with title "hello" and content "world".
    """
    posts = read_posts()
    title_query = request.args.get('title', '').strip().lower()
    content_query = request.args.get('content', '').strip().lower()

    filtered_posts = [
        post for post in posts
        if (title_query.lower() in post.get('title').lower() if title_query else True)
        and
        (content_query.lower() in post.get(
            'content').lower() if content_query else True)
    ]
    return jsonify(filtered_posts), 200


@app.route('/api/v1/posts/<int:post_id>/like', methods=['POST'])
def like(post_id):
    """
    POST /api/v1/posts/<int:post_id>/like
    Likes a given post.

    Parameters:
        post_id (int): The ID of the post to like.

    Returns:
        A JSON object containing a message and the updated number of likes.

    Example:
        POST /api/v1/posts/1/like
        Returns a JSON object with a message and the updated number of likes.
    """
    posts = read_posts()
    post = find_post_by_id(post_id, posts)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    post['likes'] = post.get('likes', 0) + 1
    save_posts(posts)
    return jsonify({"message": "Post liked!", "likes": post['likes']}), 200


@app.route('/api/v1/posts/<int:post_id>/dislike', methods=['POST'])
def dislike(post_id):
    """
    POST /api/v1/posts/<int:post_id>/dislike
    Dislikes a given post.

    Parameters:
        post_id (int): The ID of the post to dislike.

    Returns:
        A JSON object containing a message and the updated number of dislikes.

    Example:
        POST /api/v1/posts/1/dislike
        Returns a JSON object with a message and the updated number of dislikes.
    """
    posts = read_posts()
    post = find_post_by_id(post_id, posts)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    post['dislikes'] = post.get('dislikes', 0) + 1
    save_posts(posts)
    return jsonify({"message": "Post dislike!", "dislikes": post['dislikes']}), 200


@app.route('/api/v1/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    """
    POST /api/v1/posts/<int:post_id>/comments
    Adds a comment to a given post.

    Parameters:
        post_id (int): The ID of the post to add the comment to.

    Returns:
        A JSON object containing the newly added comment.

    Example:
        POST /api/v1/posts/1/comments
        Returns a JSON object containing the newly added comment.
    """
    posts = read_posts()
    post = find_post_by_id(post_id, posts)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    new_comment = request.get_json()
    if not new_comment or not new_comment.get('content'):
        return jsonify({"error": "Invalid comment data"})

    post.setdefault('comments', [])

    new_comment['id'] = id_generator(post['comments'])
    new_comment['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    post['comments'].append(new_comment)

    save_posts(posts)

    return jsonify(new_comment), 201


# error handling
@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 errors.
    Returns a JSON object containing a message and status code of 404.
    """
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    """
    Handles 405 errors.
    Returns a JSON object containing a message and status code of 405.
    """
    return jsonify({"error": "Method Not Allowed"}), 405


@app.errorhandler(500)
def internal_server_error(error):
    """
    Handles 500 errors.
    Returns a JSON object containing a message and status code of 500.
    """
    return jsonify({"error": "Internal Server Error."}), 500


@app.route('/static/masterblog.json', methods=['GET'])
def serve_masterblog_json():
    """
    Serves the masterblog.json file which is used by Swagger UI to generate the documentation.

    Returns:
        The contents of the masterblog.json file.
    """
    return send_from_directory('static', 'masterblog.json')


SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog_API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
