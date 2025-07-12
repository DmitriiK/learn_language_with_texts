// Character counter for source_text textarea
document.addEventListener('DOMContentLoaded', function() {
    const sourceText = document.getElementById('source_text');
    const charCounter = document.getElementById('char-counter');
    
    function updateCharCounter() {
        const currentLength = sourceText.value.length;
        charCounter.textContent = currentLength + '/50000';
        
        // Change color when approaching the limit
        if (currentLength >= 9000) {
            charCounter.style.color = 'red';
        } else {
            charCounter.style.color = '#659';
        }
    }
    
    // Update character count on page load
    updateCharCounter();
    
    // Update character count when user types
    sourceText.addEventListener('input', updateCharCounter);

    // Handle lemmatization checkbox changes
    const lemmatization = document.getElementById('lemmatization');
    const filterContainer = document.getElementById('filter-stopwords-container');
    lemmatization.addEventListener('change', function() {
        filterContainer.style.display = this.checked ? '' : 'none';
    });
    // Set initial state for filter container
    filterContainer.style.display = lemmatization.checked ? '' : 'none';

    // Check authentication and display user info
    checkAuthAndDisplayUser();
});

// Authentication related functions
function checkAuthAndDisplayUser() {
    fetch('/api/current_user')
        .then(response => {
            if (!response.ok) {
                throw new Error('Not authenticated');
            }
            return response.json();
        })
        .then(user => {
            document.getElementById('username').textContent = `${user.username}`;
            document.getElementById('user-role').textContent = `(${user.role})`;
            document.getElementById('user-info').style.display = 'block';
        })
        .catch(() => {
            window.location.href = '/login';
        });
}

function logout() {
    fetch('/api/logout', { method: 'POST' })
        .then(() => {
            window.location.href = '/login';
        });
}

// Form submission handler
document.getElementById('translate-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const sourceText = document.getElementById('source_text').value;
    const targetLanguage = document.getElementById('target_language').value;
    const outputFormat = document.getElementById('output_format').value;
    const layout = document.getElementById('layout').value;
    const numberOfQuestions = parseInt(document.getElementById('number_of_questions').value) || 2;
    const lemmatization = document.getElementById('lemmatization').checked;
    const filterOutStopWords = document.getElementById('filter_out_stop_words')?.checked || false;

    const requestData = {
        source_text: sourceText,
        target_language: targetLanguage,
        output_format: outputFormat,
        layout: layout,
        number_of_questions: numberOfQuestions,
        lemmatization: lemmatization,
        filter_out_stop_words: filterOutStopWords
    };



    if (outputFormat === 'web') {
        // Open a new page for the table
        const newWindow = window.open('/static/bilingual_result.html', '_blank');
        // Pass only requestData to the new window for result_render.js to use
        newWindow.bilingualRequestData = requestData;
    } 
    // Inside the form submit event handler, add this code to handle PDF selection
    else if (outputFormat === 'pdf') {
            try {
                // Create form data for the request
                const formData = new FormData();
                formData.append('source_text', sourceText);
                formData.append('target_language', targetLanguage);
                formData.append('layout', layout);
                
                // Show loading indicator
                document.getElementById('result').innerHTML = '<p>Generating PDF, please wait...</p>';
                
                // Fetch PDF directly - this will trigger browser's PDF viewer or download
                const response = await fetch('/api/make-pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (response.ok) {
                    // Create a blob from the PDF response
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    
                    // Create a link and trigger download
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'bilingual_text.pdf';
                    document.body.appendChild(a);
                    a.click();
                    
                    // Clean up
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    document.getElementById('result').innerHTML = '<p>PDF downloaded successfully!</p>';
                } else {
                    document.getElementById('result').innerHTML = '<p>Error generating PDF. Please try again.</p>';
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('result').innerHTML = '<p>An error occurred while generating the PDF.</p>';
            }
        }

    else if (outputFormat === 'json') {
        // Open raw JSON in a new tab
        const newWindow = window.open();
        const response = await fetch('/api/make_bilingual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        }); 

        if (response.ok) {
            const result = await response.json();
            if (lemmatization) {
                // If lemmatization is checked, fetch lemmas and show as raw JSON
                const lemmaResponse = await fetch('/api/lemmatize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: sourceText, language: targetLanguage, filter_out_stop_words: filterOutStopWords })
                });
                if (lemmaResponse.ok) {
                    const lemmaResult = await lemmaResponse.json();
                    newWindow.document.body.innerHTML = '<pre>' + JSON.stringify(lemmaResult, null, 2) + '</pre>';
                } else {
                    newWindow.document.body.innerHTML = '<p>Error loading lemma data</p>';
                }
            } else {
                newWindow.document.body.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            }
        } else {
            newWindow.document.body.innerHTML = '<p>Error loading data</p>';
        }
    }
});