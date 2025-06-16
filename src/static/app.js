document.getElementById('translate-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const source_text = document.getElementById('source_text').value;
    const target_language = document.getElementById('target_language').value;
    const output_format = document.getElementById('output_format').value;
    const layout = document.getElementById('layout').value;
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = 'Processing...';
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source_text, target_language, output_format, layout })
        });
        const data = await response.json();
        if (data.error) {
            resultDiv.innerHTML = `<span style='color:red'>${data.error}</span>`;
        } else if (output_format === 'web') {
            // TODO: Render result according to layout
            resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else if (output_format === 'pdf') {
            // TODO: Implement PDF download
            resultDiv.innerHTML = 'PDF download not implemented yet.';
        }
    } catch (err) {
        resultDiv.innerHTML = `<span style='color:red'>${err}</span>`;
    }
});
