document.getElementById('theme-switcher').addEventListener('click', function() {
    var body = document.body;
    if (body.classList.contains('light-theme')) {
        body.classList.remove('light-theme');
        this.classList.remove('light-theme');
        var passwordToggleIcons = document.querySelectorAll('.toggle-password');
        passwordToggleIcons.forEach(function(icon) {
            icon.style.filter = 'invert(0%)';
        });
    } else {
        body.classList.add('light-theme');
        this.classList.add('light-theme');
        var passwordToggleIcons = document.querySelectorAll('.toggle-password');
        passwordToggleIcons.forEach(function(icon) {
            icon.style.filter = 'invert(100%)';
        });
    }
});

function sanitizeHTML(str) {
    var temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

document.getElementById('chatform').addEventListener('submit', async function(event) {
    event.preventDefault();
    var messageBox = document.getElementById('message');
    var chatBox = document.getElementById('chatbox');
    var message = messageBox.value;
    messageBox.value = '';
    var userMessage = sanitizeHTML(message);
    // chatBox.innerHTML += `<p class="user-text">You: ${message.replace(/\n/g, '<br>')}</p>`;
    chatBox.innerHTML += `<p class="user-text">You: ${userMessage.replace(/\n/g, '<br>')}</p>`;

    // Send the message to the server and get the response
    var response = await fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({message: message})
    });
    var data = await response.json();

    // Display the response
    var gptResponse = sanitizeHTML(data.response);
    // chatBox.innerHTML += `<p class="gpt-text">ChatGPT: ${data.response.replace(/\n/g, '<br>')}</p>`;
    chatBox.innerHTML += `<p class="gpt-text">ChatGPT: ${gptResponse.replace(/\n/g, '<br>')}</p>`;
    // This part is inside the function that handles the server response.
    // Assuming that "data" is the variable that contains the server response.
    document.getElementById("token-count").innerText = "Tokens: " + data.output_counter;

    // If there are recommendations, display them
    if (data.recommendations) {
        var recommendList = document.getElementById('recommend-list');
        
        // Clear the existing recommendations
        recommendList.innerHTML = "";
    
        // Add the initial message
        var initialMessage = document.createElement('p');
        initialMessage.textContent = data.recommendations[0]; // "次に推奨される質問は次のようなものが考えられます。"
        recommendList.appendChild(initialMessage);
        
        // Add the recommendations
        data.recommendations.slice(1).forEach(function(rec) { // Skip the first item
            var listItem = document.createElement('li');
            
            // Remove the prefix (like "1. ", "2. ", etc.)
            var cleanRec = rec.replace(/^\d+\.\s*/, '');
            
            listItem.textContent = cleanRec;
            listItem.addEventListener('click', function() {
                document.getElementById('message').value = this.textContent;
            });
            recommendList.appendChild(listItem);
        });
    }

    // If there are wiki-searchations, display them
    if (data.wiki_search) {
        var wiki_searchList = document.getElementById('wiki-search-list');
        
        // Clear the existing wiki_search
        wiki_searchList.innerHTML = "";
        
        // Add the initial message
        var initialMessage = document.createElement('p');
        initialMessage.textContent = data.wiki_search[0];
        wiki_searchList.appendChild(initialMessage);
        
        // Add the wiki_search
        data.wiki_search.slice(1).forEach(function(rec) { // Skip the first item
            var listItem = document.createElement('li');
            
            // Remove the prefix (like "1. ", "2. ", etc.)
            var cleanRec = rec.replace(/^\d+\.\s*/, '');
            
            listItem.textContent = cleanRec;
            listItem.addEventListener('click', function() {
                document.getElementById('message').value = this.textContent;
            });
            wiki_searchList.appendChild(listItem);
        });
    }

    // 追加
    if (data.bing_search) {
        var bing_searchList = document.getElementById('bing-search-list');
        
        // Clear the existing bing_search
        bing_searchList.innerHTML = "";
        
        // Add the initial message
        var initialMessage = document.createElement('p');
        initialMessage.textContent = data.bing_search[0];
        bing_searchList.appendChild(initialMessage);
        
        // Add the bing_search
        data.bing_search.slice(1).forEach(function(rec) { // Skip the first item
            var listItem = document.createElement('li');
            
            // Remove the prefix (like "1. ", "2. ", etc.)
            var cleanRec = rec.replace(/^\d+\.\s*/, '');
            
            listItem.textContent = cleanRec;
            listItem.addEventListener('click', function() {
                document.getElementById('message').value = this.textContent;
            });
            bing_searchList.appendChild(listItem);
        });
    }

    if (data.rec_bing_search) {
        var rec_bing_searchList = document.getElementById('rec-bing-search-list');
        
        // Clear the existing bing_search
        rec_bing_searchList.innerHTML = "";
        
        // Add the initial message
        var initialMessage = document.createElement('p');
        initialMessage.textContent = data.rec_bing_search[0];
        rec_bing_searchList.appendChild(initialMessage);
        
        // Add the bing_search
        data.rec_bing_search.slice(1).forEach(function(rec) { // Skip the first item
            var listItem = document.createElement('li');
            
            // Remove the prefix (like "1. ", "2. ", etc.)
            var cleanRec = rec.replace(/^\d+\.\s*/, '');
            
            listItem.textContent = cleanRec;
            listItem.addEventListener('click', function() {
                document.getElementById('message').value = this.textContent;
            });
            rec_bing_searchList.appendChild(listItem);
        });
    }

    if (data.strage_search) {
        var strage_searchList = document.getElementById('strage-search-list');
        
        // Clear the existing bing_search
        strage_searchList.innerHTML = "";
        
        // Add the initial message
        var initialMessage = document.createElement('p');
        initialMessage.textContent = data.strage_search[0];
        strage_searchList.appendChild(initialMessage);
        
        // Add the bing_search
        data.strage_search.slice(1).forEach(function(rec) { // Skip the first item
            var listItem = document.createElement('li');
            
            // Remove the prefix (like "1. ", "2. ", etc.)
            var cleanRec = rec.replace(/^\d+\.\s*/, '');
            
            listItem.textContent = cleanRec;
            listItem.addEventListener('click', function() {
                document.getElementById('message').value = this.textContent;
            });
            strage_searchList.appendChild(listItem);
        });
    }

    chatBox.scrollTop = chatBox.scrollHeight;
});


// Add an event listener to the textarea
document.getElementById('message').addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        document.getElementById('chatform').dispatchEvent(new Event('submit'));
    }
});

document.getElementById('settingsform').addEventListener('submit', async function(event) {
    event.preventDefault();
    var modelInput = document.getElementById('model');
    var temperatureInput = document.getElementById('temperature');
    var apiKeyInput = document.getElementById('api_key');
    var bingKeyInput = document.getElementById('bing_search_v7_subscription_key'); // 新たに追加
    var bingEndpointInput = document.getElementById('bing_search_v7_endpoint'); // 新たに追加
    var strage_search_service_name = document.getElementById('search_service_name'); // 新たに追加
    var strage_index_name = document.getElementById('index_name'); // 新たに追加
    var strage_search_key = document.getElementById('strage_search_key'); // 新たに追加
    var model = modelInput.value;
    var temperature = temperatureInput.value;
    var apiKey = apiKeyInput.value;
    var bingKey = bingKeyInput.value; // 新たに追加
    var bingEndpoint = bingEndpointInput.value; // 新たに追加
    var strage_name = strage_search_service_name.value; // 新たに追加
    var strage_i_name = strage_index_name.value; // 新たに追加
    var strage_s_key = strage_search_key.value; // 新たに追加

    // Send the new settings to the server
    var response = await fetch('/update_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({model: model, temperature: temperature, api_key: apiKey, bing_search_v7_subscription_key: bingKey, bing_search_v7_endpoint: bingEndpoint, search_service_name: strage_name, index_name: strage_i_name, strage_search_key: strage_s_key}) // 新たに追加
    });
    var data = await response.json();

    // If the update was successful, update the placeholders with the new values
    if (data.status === 'success') {
        modelInput.value = model;
        temperatureInput.value = temperature;
        apiKeyInput.value = apiKey;
        bingKeyInput.value = bingKey; // 新たに追加
        bingEndpointInput.value = bingEndpoint; // 新たに追加
        strage_search_service_name.value = strage_name;
        strage_index_name.value = strage_i_name;
    }
});

// クリックイベントリスナー
document.getElementById('settings-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.add('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('open-interpreter-button').classList.remove('active');
    document.getElementById('rec-bing-search-button').classList.remove('active');
    document.getElementById('wiki-searchations-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.remove('active');
    document.getElementById('strage-search-button').classList.remove('active');
    document.getElementById('strage-search-content').style.display = 'none';
    document.getElementById('settings-content').style.display = 'block';
    document.getElementById('recommend-content').style.display = 'none';
    document.getElementById('open-interpreter-content').style.display = 'none';
    document.getElementById('rec-bing-search-content').style.display = 'none';
    document.getElementById('wiki-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'none';
});

document.getElementById('recommend-checkbox').addEventListener('change', async function(event) {
    var shouldRecommend = event.target.checked;

    // shouldRecommendの結果をデバッグ
    // console.log(shouldRecommend);
    // Send the new settings to the server
    var response = await fetch('/update_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({should_recommend: shouldRecommend})
    });
    var data = await response.json();

    // If the update was successful, log it to the console
    if (data.status === 'success') {
        console.log("Recommendation status updated successfully");
    }
});

// 追加
document.getElementById('recommendations-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('recommendations-button').classList.add('active');
    document.getElementById('open-interpreter-button').classList.remove('active');
    document.getElementById('rec-bing-search-button').classList.remove('active');
    document.getElementById('wiki-searchations-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.remove('active');
    document.getElementById('strage-search-button').classList.remove('active');
    document.getElementById('strage-search-content').style.display = 'none';
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'block';
    document.getElementById('open-interpreter-content').style.display = 'none';
    document.getElementById('rec-bing-search-content').style.display = 'none';
    document.getElementById('wiki-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'none';
});

document.getElementById('wiki-search-checkbox').addEventListener('change', async function(event) {
    var shouldRecommendWiki = event.target.checked;

    // shouldRecommendの結果をデバッグ
    // console.log(shouldRecommend);
    // Send the new settings to the server
    var response = await fetch('/update_wiki_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({should_recommend_wiki: shouldRecommendWiki})
    });

    var data = await response.json();

    if (data.status === 'success') {
        console.log("Wiki Recommendation status updated successfully");
    }
});

// 追加
document.getElementById('wiki-searchations-button').addEventListener('click', function() {
    document.getElementById('wiki-searchations-button').classList.add('active');
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('open-interpreter-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.remove('active');
    document.getElementById('rec-bing-search-button').classList.remove('active');
    document.getElementById('strage-search-button').classList.remove('active');
    document.getElementById('strage-search-content').style.display = 'none';
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'none';
    document.getElementById('open-interpreter-content').style.display = 'none';
    document.getElementById('wiki-search-content').style.display = 'block';
    document.getElementById('rec-bing-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'none';
});
// 追加
document.querySelectorAll('.toggle-password').forEach(function(toggle) {
    toggle.addEventListener('click', function(e) {
        var passwordInput = e.target.previousElementSibling;
        var passwordIcon = e.target;
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            passwordIcon.classList.remove('fa-eye');
            passwordIcon.classList.add('fa-eye-slash'); // change to eye-slash when password is visible
        } else {
            passwordInput.type = 'password';
            passwordIcon.classList.remove('fa-eye-slash');
            passwordIcon.classList.add('fa-eye'); // change to eye when password is hidden
        }
    });
});

// 追加
document.getElementById('bing-search-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('open-interpreter-button').classList.remove('active');
    document.getElementById('wiki-searchations-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.add('active');
    document.getElementById('rec-bing-search-button').classList.remove('active');
    document.getElementById('strage-search-button').classList.remove('active');
    document.getElementById('strage-search-content').style.display = 'none';
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'none';
    document.getElementById('open-interpreter-content').style.display = 'none';
    document.getElementById('wiki-search-content').style.display = 'none';
    document.getElementById('rec-bing-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'block';
});

// 追加
document.getElementById('bing-search-checkbox').addEventListener('change', async function(event) {
    var shouldRecommendBing = event.target.checked;

    // shouldRecommendBingの結果をデバッグ
    // console.log(shouldRecommendBing);
    // Send the new settings to the server
    var response = await fetch('/update_bing_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({should_recommend_bing: shouldRecommendBing})
    });

    var data = await response.json();

    if (data.status === 'success') {
        console.log("Bing Recommendation status updated successfully");
    }
});

document.getElementById('rec-bing-search-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('open-interpreter-button').classList.remove('active');
    document.getElementById('wiki-searchations-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.remove('active');
    document.getElementById('rec-bing-search-button').classList.add('active');
    document.getElementById('strage-search-button').classList.remove('active');
    document.getElementById('strage-search-content').style.display = 'none';
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'none';
    document.getElementById('open-interpreter-content').style.display = 'none';
    document.getElementById('wiki-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'none';
    document.getElementById('rec-bing-search-content').style.display = 'block';
});

document.getElementById('rec-bing-search-checkbox').addEventListener('change', async function(event) {
    var shouldRecommendrecBing = event.target.checked;

    var response = await fetch('/update_rec_bing_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({should_recommend_rec_bing: shouldRecommendrecBing})
    });

    var data = await response.json();

    if (data.status === 'success') {
        console.log("Bing Recommendation status updated successfully");
    }
});

document.getElementById('strage-search-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('open-interpreter-button').classList.remove('active');
    document.getElementById('wiki-searchations-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.remove('active');
    document.getElementById('rec-bing-search-button').classList.remove('active');
    document.getElementById('strage-search-button').classList.add('active');
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'none';
    document.getElementById('open-interpreter-content').style.display = 'none';
    document.getElementById('wiki-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'none';
    document.getElementById('rec-bing-search-content').style.display = 'none';
    document.getElementById('strage-search-content').style.display = 'block';
});

document.getElementById('strage-search-checkbox').addEventListener('change', async function(event) {
    var shouldStrageSearch = event.target.checked;

    // shouldRecommendBingの結果をデバッグ
    // console.log(shouldRecommendBing);
    // Send the new settings to the server
    var response = await fetch('/update_strage_search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({should_strage_search: shouldStrageSearch})
    });

    var data = await response.json();

    if (data.status === 'success') {
        console.log("Strage Search updated successfully");
    }
});


document.getElementById('open-interpreter-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('open-interpreter-button').classList.add('active');
    document.getElementById('wiki-searchations-button').classList.remove('active');
    document.getElementById('bing-search-button').classList.remove('active');
    document.getElementById('rec-bing-search-button').classList.remove('active');
    document.getElementById('strage-search-button').classList.remove('active');
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'none';
    document.getElementById('open-interpreter-content').style.display = 'block';
    document.getElementById('wiki-search-content').style.display = 'none';
    document.getElementById('bing-search-content').style.display = 'none';
    document.getElementById('rec-bing-search-content').style.display = 'none';
    document.getElementById('strage-search-content').style.display = 'none';
});

document.getElementById('open-interpreter-checkbox').addEventListener('change', async function(event) {
    var should_OpenInterpreter = event.target.checked;

    // shouldRecommendBingの結果をデバッグ
    // console.log(shouldRecommendBing);
    // Send the new settings to the server
    var response = await fetch('/open_interpreter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({should_open_interpreter: should_OpenInterpreter})
    });

    var data = await response.json();

    if (data.status === 'success') {
        console.log("Open_interpreter updated successfully");
    }
});
