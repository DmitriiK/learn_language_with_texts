document.getElementById('translate-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const source_text = document.getElementById('source_text').value;
    const target_language = document.getElementById('target_language').value;
    const output_format = document.getElementById('output_format').value;
    const layout = document.getElementById('layout').value;
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '';
    spinner.style.display = 'block'; // Show spinner
    try {
        const actions = {
            web: () => {
            const params = new URLSearchParams({ source_text, target_language, layout }).toString();
            window.open(`/static/bilingual_result.html?${params}`, '_blank');
            resultDiv.innerHTML = 'Opened bilingual text in a new window.';
            },
            json: () => {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/api/make_bilingual';
            form.target = '_blank';
            form.style.display = 'none';
            const addField = (name, value) => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = name;
                input.value = value;
                form.appendChild(input);
            };
            addField('source_text', source_text);
            addField('target_language', target_language);
            addField('output_format', 'json');
            addField('layout', layout);
            document.body.appendChild(form);
            form.submit();
            document.body.removeChild(form);
            resultDiv.innerHTML = '';
            },
            pdf: async () => {
            const response = await fetch('/api/make_bilingual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_text, target_language, output_format, layout })
            });
            const data = await response.json();
            if (data.error) {
                resultDiv.innerHTML = `<span style='color:red'>${data.error}</span>`;
            } else {
                resultDiv.innerHTML = 'PDF download not implemented yet.';
            }
            },
            default: async () => {
            const response = await fetch('/api/make_bilingual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_text, target_language, output_format, layout })
            });
            const data = await response.json();
            if (data.error) {
                resultDiv.innerHTML = `<span style='color:red'>${data.error}</span>`;
            }
            }
        };

        if (actions[output_format]) {
            await actions[output_format]();
        } else {
            await actions.default();
        }
    } catch (err) {
        resultDiv.innerHTML = `<span style='color:red'>${err}</span>`;
    } finally {
        spinner.style.display = 'none'; // Hide spinner
    }
});

// 1) Symbol count display
const sourceTextArea = document.getElementById('source_text');
const symbolCountDiv = document.createElement('div');
symbolCountDiv.id = 'symbol-count';
symbolCountDiv.style.marginTop = '0.5em';
sourceTextArea.parentNode.insertBefore(symbolCountDiv, sourceTextArea.nextSibling);

function updateSymbolCount() {
    symbolCountDiv.textContent = `Symbols: ${sourceTextArea.value.length}`;
}
sourceTextArea.addEventListener('input', updateSymbolCount);
updateSymbolCount();

// 2) Spinner element
const spinner = document.createElement('div');
spinner.id = 'spinner';
spinner.style.display = 'none';
spinner.innerHTML = `<div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 32px; height: 32px; animation: spin 1s linear infinite; margin: 1em auto;"></div>`;
document.body.appendChild(spinner);

// Add spinner CSS animation
const style = document.createElement('style');
style.innerHTML = `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`;
document.head.appendChild(style);
