function createTweetHTML(recommendation) {
    const media_urls = JSON.parse(recommendation.tweet.media_urls.replace(/'/g, "\""));
    const included_urls = JSON.parse(recommendation.tweet.included_urls.replace(/'/g, "\""));

    return `
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h5 class="card-title">${recommendation.tweet.id}</h5>
        <p class="card-text">${recommendation.tweet.text}</p>
        <p class="card-text"><small class="text-muted">${recommendation.tweet.created_at}</small></p>
      </div>
      <ul class="list-group list-group-flush">
        <li class="list-group-item">Retweet Count: ${recommendation.tweet.retweet_count}</li>
        <li class="list-group-item">Favorite Count: ${recommendation.tweet.favorite_count}</li>
        <li class="list-group-item">Tweet URL: <a href="${recommendation.tweet.tweet_url}">${recommendation.tweet.tweet_url}</a></li>
        <li class="list-group-item">Media URLs: ${media_urls.join(', ')}</li>
        ${media_urls.map(url => `<li class="list-group-item"><a href="${url}" target="_blank"><img src="${url}" class="tweet-image img-thumbnail"/></a></li>`).join('')}
        <li class="list-group-item">Included URLs: ${included_urls.join(', ')}</li>
      </ul>
    </div>`;

}


document.addEventListener('DOMContentLoaded', () => {
    fetch('http://127.0.0.1:8000/data/recommendations/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('HTTP error ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        const tweetsContainer = document.getElementById('tweetsContainer');
        let htmlString = '';
        data.forEach(recommendation => {
            htmlString += createTweetHTML(recommendation);
        });
        tweetsContainer.innerHTML = htmlString;
    })
    .catch(error => console.error('Error:', error));
});
