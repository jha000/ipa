// JavaScript code for handling the IPA conversion and language selection

const uploadArea = document.getElementById('upload-area');
const audioUpload = document.getElementById('audio-upload');
const fileList = document.getElementById('file-list');
const convertBtn = document.getElementById('convert-btn');
const outputDiv = document.getElementById('output');
const hindiOutputDiv = document.getElementById('hindi-output');
const englishOutputDiv = document.getElementById('english-output');
const bengaliOutputDiv = document.getElementById('bengali-output');
const errorDiv = document.getElementById('error');
const loadingDiv = document.getElementById('loading');
const copyBtn = document.getElementById('copy-btn');
const languageSelect = document.getElementById('language-select');
const languageContainer = document.querySelector('.language-container');


uploadArea.addEventListener('click', () => {
    audioUpload.click();
});

audioUpload.addEventListener('change', () => {
    const files = audioUpload.files;
    handleFiles(files);
});

copyBtn.addEventListener('click', () => {
    const selectedViewer = document.querySelector('.ipa-viewer .terminal-output:not([style*="display: none"])');
    if (selectedViewer && selectedViewer.textContent.trim() !== '') {
        const range = document.createRange();
        range.selectNode(selectedViewer);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        window.getSelection().removeAllRanges();

        copyBtn.textContent = 'Copied';
        setTimeout(() => {
            copyBtn.textContent = 'Copy';
        }, 3000);
    }
});


languageSelect.addEventListener('change', () => {
    showSelectedLanguageText(languageSelect.value);
});

function handleFiles(files) {
    fileList.innerHTML = '';
    outputDiv.textContent = '';
    hindiOutputDiv.textContent = '';
    englishOutputDiv.textContent = '';
    bengaliOutputDiv.textContent = '';
    errorDiv.textContent = '';
    copyBtn.style.display = 'none';
    languageContainer.style.display = 'none';

    languageSelect.value = '';

    for (const file of files) {
        const listItem = document.createElement('div');
        listItem.classList.add('file-item');

        const fileHeading = document.createElement('h3');
        fileHeading.textContent = 'Uploaded File:';
        listItem.appendChild(fileHeading);

        const fileName = document.createElement('span');
        fileName.textContent = file.name;
        const fileSize = document.createElement('span');
        fileSize.textContent = ` (${(file.size / 1024).toFixed(2)} KB)`;

        listItem.appendChild(fileName);
        listItem.appendChild(fileSize);
        fileList.appendChild(listItem);
    }

    convertBtn.style.display = 'block';
}

convertBtn.addEventListener('click', () => {
    loadingDiv.style.display = 'block';
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
            loadingDiv.style.display = 'none';
            if (data.ipa) {
                outputDiv.textContent = `${data.ipa}`;
                hindiOutputDiv.textContent = `${data.hindi}`;
                englishOutputDiv.textContent = `${data.english}`;
                bengaliOutputDiv.textContent = `${data.bengali}`;
                errorDiv.textContent = '';
                copyBtn.style.display = 'block';
                languageContainer.style.display = 'block';

                // Show only IPA by default after conversion
                outputDiv.style.display = 'block';
                hindiOutputDiv.style.display = 'none';
                englishOutputDiv.style.display = 'none';
                bengaliOutputDiv.style.display = 'none';
            } else if (data.error) {
                errorDiv.textContent = `Error: ${data.error}`;
                copyBtn.style.display = 'none';
                languageContainer.style.display = 'none';
            }
        })
        .catch(error => {
            loadingDiv.style.display = 'none';
            errorDiv.textContent = `Error: ${error.message}`;
            copyBtn.style.display = 'none';
        });
    }
}

function showSelectedLanguageText(selectedLanguage) {
    outputDiv.style.display = 'none';
    hindiOutputDiv.style.display = 'none';
    englishOutputDiv.style.display = 'none';
    bengaliOutputDiv.style.display = 'none';

    switch (selectedLanguage) {
        case 'en':
            englishOutputDiv.style.display = 'block';
            break;
        case 'hi':
            hindiOutputDiv.style.display = 'block';
            break;
        case 'bn':
            bengaliOutputDiv.style.display = 'block';
            break;
        default:
            outputDiv.style.display = 'block';
            break;
    }
}
