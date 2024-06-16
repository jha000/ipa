const uploadArea = document.getElementById('upload-area');
const audioUpload = document.getElementById('audio-upload');
const fileList = document.getElementById('file-list');
const convertBtn = document.getElementById('convert-btn');
const outputDiv = document.getElementById('output');
const errorDiv = document.getElementById('error');
const loadingDiv = document.getElementById('loading');

uploadArea.addEventListener('click', () => {
    audioUpload.click();
});

audioUpload.addEventListener('change', () => {
    const files = audioUpload.files;
    handleFiles(files);
});

function handleFiles(files) {
    fileList.innerHTML = ''; // Clear previous file list
    outputDiv.textContent = ''; // Clear previous IPA text
    errorDiv.textContent = ''; // Clear previous error message

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
            } else {
                outputDiv.textContent = '';
                errorDiv.textContent = data.error || 'Error converting audio to IPA.';
            }
        })
        .catch(error => {
            loadingDiv.style.display = 'none'; // Hide loading animation
            outputDiv.textContent = '';
            errorDiv.textContent = 'Error uploading audio file.';
            console.error('Error:', error);
        });
    }
}
