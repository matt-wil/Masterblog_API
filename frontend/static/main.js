// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';

                // Add Timestamp for created and dynamically for updated.
                let timestamps = `<p style="font-size: 12px;">Created: ${post.date}</p>`;
                if (post.updated_at) {
                    timestamps += `<p style="font-size: 12px;">Updated: ${post.updated_at}</p>`;
                }

                // Generate comments
                let commentsHtml = `
                <div class="comments">
                    <h4>Comments</h4>
                        ${post.comments?.map(comment => `<p><strong>${comment.author}:</strong> ${comment.content}</p>`).join('') || ''}
                        <input type="text" id="comment-${post.id}" placeholder="Add a comment">
                        <button onclick="addComment(${post.id})" style="background-color: #4CAF50;">Add Comment</button>
                </div>`;


                postDiv.innerHTML = `<h2>${post.title}</h2><p>${post.content}</p><p style="font-size: 14px;">Tags: ${post.tags}</p><p style="font-size: 12px;">Author: ${post.author}</p>
                ${timestamps}
                <button onclick="updatePost(${post.id})" style="background-color: #FFA500;">Update</button>
                <button onclick="deletePost(${post.id})">Delete</button>
                <p>
                    <span class="likes-count">${post.likes || 0}</span>
                    <img src="static/assets/heart-solid.svg" style="width: 16px; height: 16px;">
                    <button onclick="likePost(${post.id})" style="background-color: #4CAF50">
                        Like
                    </button>
                    <span class="dislikes-count">${post.dislikes || 0}</span>
                    <img src="static/assets/heart-crack-solid.svg" style="width: 16px; height: 16px;">
                    <button onclick="dislikePost(${post.id})">
                        Dislike
                    </button>
                </p>
                ${commentsHtml}`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postTags = document.getElementById('post-tags').value;

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
        title: postTitle,
        content: postContent,
        author: postAuthor,
        tags: postTags
        })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

function likePost(postId) {
    const baseUrl = document.getElementById('api-base-url').value;
    fetch(`${baseUrl}/posts/${postId}/like`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Post liked:', data);
            loadPosts();
        })
        .catch(error => console.error('Error liking post', error));
}

function dislikePost (postId) {
    const baseUrl = document.getElementById('api-base-url').value;
    fetch(`${baseUrl}/posts/${postId}/dislike`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Post disliked:', data);
            loadPosts();
        })
        .catch(error => console.error('Error disliking post:', error));
}

function addComment(postId) {
    const baseUrl = document.getElementById('api-base-url').value;
    const commentContent = document.getElementById(`comment-${postId}`).value;

    fetch(`${baseUrl}/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author: 'Anonymous', content: commentContent })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Comment added:', data);
            loadPosts();
        })
        .catch(error => console.error('Error adding comment', error));
}

function updatePost(postId) {
    const baseUrl = document.getElementById('api-base-url').value;
    const newTitle = prompt('Enter a new title:');
    const newContent = prompt('Enter new content:');

    fetch(`${baseUrl}/posts/${postId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, content: newContent })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Post updated:', data);
            loadPosts();
        })
        .catch(error => console.error('Error updating post:', error));
}