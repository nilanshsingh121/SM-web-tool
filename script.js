function showTab(n) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${n}`).classList.add('active');
    document.querySelectorAll('.tab-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === n);
    });
}

// Study Planner
document.getElementById('study-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const subjects = document.getElementById('subjects').value.trim();
    const examDate = document.getElementById('exam-date').value;

    const resultsContainer = document.getElementById('results-container');
    const studyPlanDiv = document.getElementById('study-plan');

    studyPlanDiv.innerHTML = '<p>Generating your plan...</p>';
    resultsContainer.style.display = 'block';

    try {
        const res = await fetch('/generate_plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subjects, exam_date: examDate })
        });
        const data = await res.json();

        if (res.ok) {
            let html = '';
            for (const day in data.plan) {
                html += `<div class="plan-item"><strong>${day}:</strong> ${data.plan[day]}</div>`;
            }
            studyPlanDiv.innerHTML = html;
        } else {
            studyPlanDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
        }
    } catch (err) {
        studyPlanDiv.innerHTML = '<p style="color:red;">Something went wrong. Try again.</p>';
    }
});

// PDF Upload
async function uploadPDF() {
    const file = document.getElementById('pdf-input').files[0];
    if (!file) return alert('Please select a PDF file');

    const formData = new FormData();
    formData.append('pdf', file);

    try {
        const res = await fetch('/upload_pdf', { method: 'POST', body: formData });
        const data = await res.json();
        showResourceResults(data);
    } catch (err) {
        alert('Error processing PDF');
    }
}

// Video Processing
async function processVideo() {
    const url = document.getElementById('video-url').value.trim();
    if (!url) return alert('Please enter a video URL');

    try {
        const res = await fetch('/process_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await res.json();
        showResourceResults(data);
    } catch (err) {
        alert('Error processing video');
    }
}

function showResourceResults(data) {
    const container = document.getElementById('resource-results');
    let html = `<h3>? Analysis Ready</h3>`;
    html += `<h4>Summary</h4><p>${data.summary}</p>`;
    
    html += `<h4>Flashcards</h4>`;
    data.flashcards.forEach(fc => {
        html += `<div class="flashcard" onclick="this.innerHTML = '<strong>Answer:</strong> ${fc.a}'">${fc.q}</div>`;
    });

    html += `<h4>Smart Notes</h4><pre>${data.notes}</pre>`;
    container.innerHTML = html;
}