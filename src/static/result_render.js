// Functions for rendering bilingual content
function renderContinuous(bilingual) {
    let html = '';
    for (const para of bilingual.paragraphs) {
        html += '<div class="paragraph">';
        html += '<div>';
        for (const s of para.Sintagmas) {
            const match = s.source_text.match(/([.,!?…]+)$/u);
            let punctuation = match ? match[1] : '';
            let source = s.source_text.replace(/([.,!?…]+)$/u, '');
            let target = s.target_text.replace(/([.,!?…]+)$/u, '');
            html += `<span>${source}</span>  <span class="syntagma-translation">(${target})</span>${punctuation} `;
        }
        html += '</div>';
        html += '<div style="margin-top:0.5em;font-style:italic;">';
        html += para.Sintagmas.map(s => s.source_text).join(' ');
        html += '</div></div><br>';
    }
    return html;
}

function renderSideBySide(bilingual) {
    let html = '<table><tr><th>Source</th><th>Translation</th></tr>';
    for (const para of bilingual.paragraphs) {
        for (const s of para.Sintagmas) {
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

// Only run this if on the bilingual result page
async function loadBilingualResult() {
    // Get params from window.name or localStorage or another method if needed
    // For now, expect window.bilingualRequestData to be set by opener
    if (!window.bilingualRequestData) return;
    const requestData  = window.bilingualRequestData;
    const response = await fetch('/api/make_bilingual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });
    if (response.ok) {
        const end_point_data = await response.json();
        document.getElementById('bilingual-content').innerHTML = renderBilingual(end_point_data, layout);
    } else {
        document.body.innerHTML = '<p>Error loading data</p>';
    }
}

if (window.location.pathname.endsWith('bilingual_result.html')) {
    window.addEventListener('DOMContentLoaded', loadBilingualResult);
}
