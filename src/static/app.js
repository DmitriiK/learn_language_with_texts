document.getElementById('translate-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const sourceText = document.getElementById('source_text').value;
    const targetLanguage = document.getElementById('target_language').value;
    const outputFormat = document.getElementById('output_format').value;
    const layout = document.getElementById('layout').value;
    const lemmatization = document.getElementById('lemmatization').checked;

    const requestData = {
        source_text: sourceText,
        target_language: targetLanguage,
        output_format: outputFormat,
        layout: layout,
        lemmatization: lemmatization
    };

    if (outputFormat === 'web') {
        // Open a new page for the table
        const newWindow = window.open('/static/bilingual_result.html', '_blank');
        // Pass only requestData to the new window for result_render.js to use
        newWindow.bilingualRequestData = requestData;
    } else if (outputFormat === 'json') {
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
                    body: JSON.stringify({ text: sourceText, language: targetLanguage })
                });
                if (lemmaResponse.ok) {
                    const lemmaResult = await lemmaResponse.json();
                    newWindow.document.write('<pre>' + JSON.stringify(lemmaResult, null, 2) + '</pre>');
                } else {
                    newWindow.document.write('<p>Error loading lemma data</p>');
                }
            } else {
                newWindow.document.write('<pre>' + JSON.stringify(result, null, 2) + '</pre>');
            }
        } else {
            newWindow.document.write('<p>Error loading data</p>');
        }
    }
});