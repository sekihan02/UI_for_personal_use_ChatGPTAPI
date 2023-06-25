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
