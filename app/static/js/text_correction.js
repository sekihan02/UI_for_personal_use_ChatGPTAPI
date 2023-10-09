document.getElementById('file-upload').addEventListener('change', handleFileUpload);
document.getElementById('drop-zone').addEventListener('drop', handleFileDrop);
document.getElementById('drop-zone').addEventListener('dragover', function(e) {
    e.preventDefault(); // Prevent default behavior of file being opened in browser
});

function handleFileUpload(e) {
    const file = e.target.files[0];
    detectEncodingAndLoadText(file);
}

function handleFileDrop(e) {
    e.preventDefault(); // Prevent default behavior of file being opened in browser
    const file = e.dataTransfer.files[0];
    detectEncodingAndLoadText(file);
}

function detectEncodingAndLoadText(file) {
    // Detect encoding
    const formData = new FormData();
    formData.append('file', file);

    fetch('/text_correction/detect_encoding', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert('Detected encoding: ' + data.encoding); // Or display it in some other way
        loadTextFromFile(file, data.encoding); // Use detected encoding to load text
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function loadTextFromFile(file, encoding) {
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('text-area').value = e.target.result;
    };
    reader.readAsText(file, encoding); // Use the detected encoding here
}

function getCaretCoordinates(elem, position) {
    const mirrorDiv = document.createElement('div');
    const style = window.getComputedStyle ? getComputedStyle(elem) : elem.currentStyle;

    mirrorDiv.style.cssText = `
        position: absolute;
        top: -99999px;
        left: -99999px;
        width: ${elem.offsetWidth}px;
        height: ${elem.offsetHeight}px;
        font-size: ${style.fontSize};
        font-family: ${style.fontFamily};
        line-height: ${style.lineHeight};
        resize: none;
    `;
    mirrorDiv.textContent = elem.value.substring(0, position);

    document.body.appendChild(mirrorDiv);

    const coordinates = {
        left: mirrorDiv.offsetWidth,
        top: mirrorDiv.offsetHeight
    };

    document.body.removeChild(mirrorDiv);

    return coordinates;
}

document.getElementById('text-area').addEventListener('mouseup', function() {
    const textarea = document.getElementById('text-area');
    const hover = document.getElementById('hover');
    const correctionSuggestions = document.getElementById('correction-suggestions');
    
    const selectedText = this.value.substring(this.selectionStart, this.selectionEnd);
    
    if(selectedText.length > 0) {
        const textareaBottom = textarea.offsetTop + textarea.offsetHeight;
        
        // ホバーエレメントの位置を設定
        hover.style.left = "50%";
        hover.style.top = textareaBottom + "px"; 
        hover.style.display = 'block';
        
        // 修正候補エレメントの位置を設定
        correctionSuggestions.style.left = "50%";
        correctionSuggestions.style.top = textareaBottom + "px";
        
    } else {
        hover.style.display = 'none';
        correctionSuggestions.style.display = 'none';
    }
});


document.getElementById('hover').addEventListener('mousedown', function(e) {
    e.preventDefault();
});

document.getElementById('correction-check').addEventListener('change', function() {
    const textarea = document.getElementById('text-area');
    const selectedText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
    
    if(this.checked && selectedText.length > 0) {
        this.checked = false;
        fetchCorrections(selectedText);
    }
});

function fetchCorrections(selectedText) {
    // Show loading overlay
    document.getElementById('loading').style.display = 'block';

    // Send text to server
    fetch('/text_correction/get_corrections', {
        method: 'POST',
        body: JSON.stringify({ text: selectedText }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading overlay
        document.getElementById('loading').style.display = 'none';

        // Show corrections in the hover
        const hover = document.getElementById('hover');
        const correctionSuggestions = document.getElementById('correction-suggestions');
        
        // 修正候補の位置をhoverエレメントに合わせる
        correctionSuggestions.style.left = hover.style.left; 
        correctionSuggestions.style.top = hover.style.top;
        
        correctionSuggestions.innerHTML = ''; // Clear previous content
        data.corrections.forEach(correction => {
            const p = document.createElement('p');
            p.innerText = correction;
            p.style.cursor = 'pointer';
            p.onclick = function() {
                // replaceSelectedText(correction);
                replaceSelectedTextInTextarea(correction);
                correctionSuggestions.style.display = 'none'; // Hide suggestions after selecting correction
                document.getElementById('hover').style.display = 'none';
            };
            correctionSuggestions.appendChild(p);
        });
        correctionSuggestions.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        // Hide loading overlay in case of error
        document.getElementById('loading').style.display = 'none';
    });
}

function replaceSelectedTextInTextarea(replacementText) {
    const textarea = document.getElementById('text-area');
    const selectionStart = textarea.selectionStart;
    const selectionEnd = textarea.selectionEnd;
    
    const before = textarea.value.substring(0, selectionStart);
    const after = textarea.value.substring(selectionEnd);
    
    textarea.value = before + replacementText + after;
    textarea.setSelectionRange(selectionStart, selectionStart + replacementText.length);
}

document.getElementById('correct-text-btn').addEventListener('click', function() {
    const text = document.getElementById('text-area').value;
    const blob = new Blob([text], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = 'corrected_text.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});
