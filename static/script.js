const uploadArea = document.getElementById('upload-area');
const audioUpload = document.getElementById('audio-upload');
const fileList = document.getElementById('file-list');
const convertBtn = document.getElementById('convert-btn');
const outputDiv = document.getElementById('output');
const errorDiv = document.getElementById('error');
const loadingDiv = document.getElementById('loading');
const copyBtn = document.getElementById('copy-btn');

uploadArea.addEventListener('click', () => {
    audioUpload.click();
});

audioUpload.addEventListener('change', () => {
    const files = audioUpload.files;
    handleFiles(files);
});

copyBtn.addEventListener('click', () => {
    // Select the text inside the typed output div
    const range = document.createRange();
    range.selectNode(outputDiv);
    window.getSelection().removeAllRanges(); // Clear previous selections
    window.getSelection().addRange(range); // Select the text
    document.execCommand('copy'); // Copy the selected text to clipboard
    window.getSelection().removeAllRanges(); // Clear the selection after copying
    
    // Change the text inside the copy button to "Copied"
    copyBtn.textContent = 'Copied';
    setTimeout(() => {
        // Reset the text inside the copy button to "Copy" after 2 seconds
        copyBtn.textContent = 'Copy';
    }, 3000); // Set the timeout for 2 seconds
});


function handleFiles(files) {
    fileList.innerHTML = ''; // Clear previous file list
    outputDiv.textContent = ''; // Clear previous IPA text
    errorDiv.textContent = ''; // Clear previous error message
    copyBtn.style.display = 'none';

    for (const file of files) {
        const listItem = document.createElement('div');
        listItem.classList.add('file-item');

        // Create a heading for the uploaded file
        const fileHeading = document.createElement('p');
        fileHeading.textContent = 'Uploaded File:';
        listItem.appendChild(fileHeading);

        // Create a span for the file name
        const fileName = document.createElement('span');
        fileName.textContent = file.name;
        const fileSize = document.createElement('span');
        fileSize.textContent = ` (${(file.size / 1024).toFixed(2)} KB)`;

        listItem.appendChild(fileName);
        listItem.appendChild(fileSize);
        fileList.appendChild(listItem);
    }

    convertBtn.style.display = 'block'; // Show convert button
}

convertBtn.addEventListener('click', () => {
    loadingDiv.style.display = 'block'; // Show loading animation
    convertAudioToIPA();
});

function convertAudioToIPA() {
    const file = audioUpload.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('audio', file);

        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingDiv.style.display = 'none'; // Hide loading animation
            if (data.ipa) {
                outputDiv.textContent = `${data.ipa}`;
                errorDiv.textContent = '';
                // Show copy button only if there is output
                copyBtn.style.display = 'block';
            } else {
                outputDiv.textContent = '';
                errorDiv.textContent = data.error || 'Error converting audio to IPA.';
                // Hide copy button if there is no output
                copyBtn.style.display = 'none';
            }
        })
        .catch(error => {
            loadingDiv.style.display = 'none'; // Hide loading animation
            outputDiv.textContent = '';
            errorDiv.textContent = 'Error uploading audio file.';
            console.error('Error:', error);
            // Hide copy button if there is an error
            copyBtn.style.display = 'none';
        });
    }
}
