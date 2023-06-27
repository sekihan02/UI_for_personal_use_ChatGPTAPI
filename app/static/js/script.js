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

document.getElementById('chatform').addEventListener('submit', async function(event) {
    event.preventDefault();
    var messageBox = document.getElementById('message');
    var chatBox = document.getElementById('chatbox');
    var message = messageBox.value;
    messageBox.value = '';
    chatBox.innerHTML += `<p class="user-text">You: ${message.replace(/\n/g, '<br>')}</p>`;

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
    chatBox.innerHTML += `<p class="gpt-text">GPT-3: ${data.response.replace(/\n/g, '<br>')}</p>`;
    
    // If there are recommendations, display them
    if (data.recommendations) {
        var recommendList = document.getElementById('recommend-list');
        
        // Clear the existing recommendations
        recommendList.innerHTML = "";
        
        // Display the new recommendations
        data.recommendations.forEach(function(rec, index) {
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
    var model = modelInput.value;
    var temperature = temperatureInput.value;
    var apiKey = apiKeyInput.value;

    // Send the new settings to the server
    var response = await fetch('/update_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({model: model, temperature: temperature, api_key: apiKey})
    });
    var data = await response.json();

    // If the update was successful, update the placeholders with the new values
    if (data.status === 'success') {
        modelInput.value = model;
        temperatureInput.value = temperature;
        apiKeyInput.value = apiKey;
    }
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

document.getElementById('settings-button').addEventListener('click', function() {
    document.getElementById('settings-button').classList.add('active');
    document.getElementById('recommendations-button').classList.remove('active');
    document.getElementById('settings-content').style.display = 'block';
    document.getElementById('recommend-content').style.display = 'none';
});

document.getElementById('recommendations-button').addEventListener('click', function() {
    document.getElementById('recommendations-button').classList.add('active');
    document.getElementById('settings-button').classList.remove('active');
    document.getElementById('settings-content').style.display = 'none';
    document.getElementById('recommend-content').style.display = 'block';
});


document.querySelector('.toggle-password').addEventListener('click', function(e) {
    var passwordInput = document.getElementById('api_key');
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
