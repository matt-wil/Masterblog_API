# Utility functions

def find_post_by_id(post_id, posts):
    """
    Find a post in a list of posts by its id.

    Args:
        post_id: The id of the post to find
        posts: The list of posts to search through

    Returns:
        The post if it is found, None otherwise
    """
    for post in posts:
        if post.get('id') == post_id:
            return post
    return None


def id_generator(posts):
    """
    Generate an id for a post based on the list of existing posts.

    The id generated is one more than the highest id in the list of posts.
    If the list of posts is empty, the id generated is 1.

    Args:
        posts: The list of posts to generate an id for

    Returns:
        An id for the post
    """
    if posts:
        return max(post['id'] for post in posts) + 1
    return 1
