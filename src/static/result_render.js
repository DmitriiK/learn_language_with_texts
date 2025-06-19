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

// Load data from query string
function getQueryParam(name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
}

async function loadAndRender() {
    const id = getQueryParam('id');
    const layout = getQueryParam('layout') || 'continuous';
    const source_text = getQueryParam('source_text');
    const target_language = getQueryParam('target_language');
    if (!source_text || !target_language) {
        document.getElementById('bilingual-content').innerHTML = '<span style="color:red">Missing parameters.</span>';
        return;
    }
    const response = await fetch('/api/make_bilingual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_text, target_language, output_format: 'json', layout })
    });
    const data = await response.json();
    if (data.error) {
        document.getElementById('bilingual-content').innerHTML = `<span style='color:red'>${data.error}</span>`;
        return;
    }
    document.getElementById('bilingual-content').innerHTML = renderBilingual(data, layout);
}

window.onload = loadAndRender;
