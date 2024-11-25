from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/api/v1/posts/<int:post_id>', methods=['GET'])
def update_post(post_id):
    pass


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
