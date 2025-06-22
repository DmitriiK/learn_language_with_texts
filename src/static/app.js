function renderContinuous(bilingual) {
    let html = '';
    for (const para of bilingual.paragraphs) {
        html += '<div class="paragraph">';
        html += '<div>';
        for (const s of para.Sintagmas) {
            // Regex to match trailing punctuation (.,!?… and similar)
            const match = s.source_text.match(/([.,!?…]+)$/u);
            let punctuation = match ? match[1] : '';
            let source = s.source_text.replace(/([.,!?…]+)$/u, '');
            let target = s.target_text.replace(/([.,!?…]+)$/u, '');
            html += `<span>${source}</span>  <span class="syntagma-translation">(${target})</span>${punctuation} `;
        }
        html += '</div>';
        html += '<div style="margin-top:0.5em;font-style:italic;">';
        html += para.Sintagmas.map(s => s.source_text).join(' ');
        html += '</div></div><br>'; // double new line
    }
    return html;
}

function renderSideBySide(bilingual) {
    let html = '<table><tr><th>Source</th><th>Translation</th></tr>';
    for (const para of bilingual.paragraphs) {
        for (const s of para.Sintagmas) {
            // Display source first, then target
            html += `<tr><td>${s.source_text}</td><td class="syntagma-translation">${s.target_text}</td></tr>`;
        }
    }
    html += '</table>';
    return html;
}

function renderBilingual(bilingual, layout) {
    if (layout === 'side-by-side') {
        return renderSideBySide(bilingual);
    } else {
        return renderContinuous(bilingual);
    }
}
document.getElementById('translate-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const sourceText = document.getElementById('source_text').value;
    const targetLanguage = document.getElementById('target_language').value;
    const outputFormat = document.getElementById('output_format').value;
    const layout = document.getElementById('layout').value;

    const requestData = {
        source_text: sourceText,
        target_language: targetLanguage,
        output_format: outputFormat,
        layout: layout   
    };

    if (outputFormat === 'web') {
        // Open a new page for the table
        const newWindow = window.open('/static/bilingual_result.html', '_blank');
        newWindow.onload = async function () {
            const response = await fetch('/api/make_bilingual', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const end_point_data = await response.json();
                // FIX: Use newWindow.document to access the element in the new window
                newWindow.document.getElementById('bilingual-content').innerHTML = renderBilingual(end_point_data, layout);
            } else {
                newWindow.document.body.innerHTML = '<p>Error loading data</p>';
            }
        };
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
            newWindow.document.write('<pre>' + JSON.stringify(result, null, 2) + '</pre>');
        } else {
            newWindow.document.write('<p>Error loading data</p>');
        }
    }
});