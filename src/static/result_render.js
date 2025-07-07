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

function renderLemmasTable(lemmas) {
    if (!lemmas || !lemmas.length) return '';
    let html = `<h2>Lemmas</h2>
        <div><b>Number of lemmas:</b> ${lemmas.length}</div>
        <table>
            <tr><th>Lemma</th><th>Number of Words</th><th>Number of Occurrences</th></tr>`;
    for (const lemma of lemmas) {
        html += `<tr><td>${lemma.lemma}</td><td>${lemma.number_of_words}</td><td>${lemma.number_of_occurrences}</td></tr>`;
    }
    html += '</table>';
    return html;
}

// Only run this if on the bilingual result page
async function loadBilingualResult() {
    // Get params from window.name or localStorage or another method if needed
    // For now, expect window.bilingualRequestData to be set by opener
    if (!window.bilingualRequestData) return;
    console.log('requesing.. ')
    const requestData  = window.bilingualRequestData;
    const response = await fetch('/api/make_bilingual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });
    if (response.ok) {
        const end_point_data = await response.json();
        window.data_hash = end_point_data.data_hash;
        console.log(end_point_data.data_hash)
        let rnd = renderBilingual(end_point_data, requestData.layout);
        document.getElementById('bilingual-content').innerHTML = rnd;
        // If lemmatization is requested, fetch lemmas and append as table
        if (requestData.lemmatization) await request_lemmanization(requestData, end_point_data); 
    } else {
        document.body.innerHTML = '<p>Error loading data</p>';
    }
}
// console.log("window.bilingualRequestData:", window.bilingualRequestData);
if (window.location.pathname.endsWith('bilingual_result.html')) {
    window.addEventListener('DOMContentLoaded', () => {
        loadBilingualResult();
        // Add event listener for audio generation form
        MakeAudioRequiestFuctionality();
    });
}
function MakeAudioRequiestFuctionality() {
    const audioForm = document.getElementById('audio-form');
    if (audioForm) {
        // Add a status element if not present
        let statusElem = document.getElementById('audio-status');
        if (!statusElem) {
            statusElem = document.createElement('div');
            statusElem.id = 'audio-status';
            statusElem.style.marginTop = '1em';
            audioForm.parentNode.appendChild(statusElem);
        }
        audioForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const audioFormat = document.getElementById('audio-format').value;
            const dataHash = window.data_hash;
            if (!dataHash) {
                statusElem.textContent = 'Data not loaded yet. Please wait for the bilingual result to load.';
                return;
            }
            statusElem.textContent = 'Generating audio, please wait...';
            // Call make_audio endpoint using GET
            try {
                // Use the correct parameter name expected by FastAPI: bilingual_text_hash
                const params = new URLSearchParams({ bilingual_text_hash: dataHash, output_format: audioFormat });

                //const xxx = `/api/make_audio?bilingual_text_hash=${bilingualTextHash}&output_format=${outputFormat}`
                console.log(params)
                const response = await fetch(`/api/make_audio?${params.toString()}`);
                if (response.ok) {
                    const result = await response.json();
                    if (result.audio_url) {
                        statusElem.innerHTML = 'Audio generated! <a href="' + result.audio_url + '" target="_blank" download>Download audio</a>';
                        // Optionally, open download window automatically
                        window.open(result.audio_url, '_blank');
                    } else {
                        statusElem.textContent = 'Audio generated, but no download link provided.';
                    }
                } else {
                    statusElem.textContent = 'Failed to generate audio.';
                }
            } catch (err) {
                statusElem.textContent = 'Error generating audio: ' + err;
            }
        });
    }
}

async function request_lemmanization(requestData, end_point_data) {
    {
        lemma_page_element = document.getElementById('lemmas-content');
        lemma_page_element.innerHTML = 'Working on preparation of frequency list..';
        const lemmaResponse = await fetch('/api/lemmatize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: requestData.source_text,
                language: end_point_data.source_language,
                filter_out_stop_words: requestData.filter_out_stop_words
            })
        });
        if (lemmaResponse.ok) {
            const lemmaData = await lemmaResponse.json();
            lemma_page_element.innerHTML = renderLemmasTable(lemmaData.lemmas);
        } else {
            lemma_page_element.innerHTML = '<p>Error loading lemma data</p>';
        }
    }
}

