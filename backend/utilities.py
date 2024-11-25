# Utility functions

def find_post_by_id(post_id, posts):
    for post in posts:
        if post.get('id') == post_id:
            return post
    return None


def id_generator(posts):
    if posts:
        return max(post['id'] for post in posts) + 1
    return 1
