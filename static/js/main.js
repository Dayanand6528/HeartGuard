/* HeartGuard Interactive Client Logic */

document.addEventListener('DOMContentLoaded', () => {
    initFloatingChatbot();
    initDedicatedChatbot();
    initPredictionForm();
    initDoctorNotes();
    initAdminRoleEditor();
});

/* Helper Markdown Formatter */
function formatMarkdownText(text) {
    if (!text) return '';
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Bold text **word**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Newlines to <br>
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

/* Helper Message Append */
function appendMsg(container, text, sender) {
    if (!container) return null;
    const div = document.createElement('div');
    const id = 'msg_' + Date.now();
    div.id = id;
    div.className = `message message-${sender}`;
    div.innerHTML = formatMarkdownText(text);
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeMsg(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

/* Floating Chatbot Widget Handler */
function initFloatingChatbot() {
    const floatBtn = document.getElementById('floatingChatBtn');
    const floatWin = document.getElementById('floatingChatWindow');
    const closeBtn = document.getElementById('closeFloatChat');
    const sendBtn = document.getElementById('sendFloatMsg');
    const input = document.getElementById('floatChatInput');
    const msgContainer = document.getElementById('floatChatMessages');

    if (!floatBtn || !floatWin) return;

    floatBtn.addEventListener('click', () => {
        floatWin.classList.toggle('active');
        if (floatWin.classList.contains('active') && input) {
            input.focus();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            floatWin.classList.remove('active');
        });
    }

    const sendHandler = async () => {
        if (!input) return;
        const text = input.value ? input.value.trim() : '';
        if (!text) return;

        appendMsg(msgContainer, text, 'user');
        input.value = '';

        const typingId = appendMsg(msgContainer, 'HeartGuard AI is analyzing...', 'bot');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            removeMsg(typingId);
            appendMsg(msgContainer, data.response, 'bot');
        } catch (e) {
            removeMsg(typingId);
            appendMsg(msgContainer, "Error connecting to medical chatbot service.", 'bot');
        }
    };

    if (sendBtn) {
        sendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            sendHandler();
        });
    }

    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendHandler();
            }
        });
    }
}

/* Dedicated Chatbot Page Handler */
function initDedicatedChatbot() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const msgContainer = document.getElementById('dedicatedChatMessages');

    if (!input && !sendBtn && !msgContainer) return;

    const handleSend = async () => {
        if (!input) return;
        const text = input.value ? input.value.trim() : '';
        if (!text) return;

        appendMsg(msgContainer, text, 'user');
        input.value = '';

        const typingId = appendMsg(msgContainer, 'HeartGuard AI analyzing query...', 'bot');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            removeMsg(typingId);
            appendMsg(msgContainer, data.response, 'bot');
        } catch (e) {
            removeMsg(typingId);
            appendMsg(msgContainer, "Error processing response. Please check backend connection.", 'bot');
        }
    };

    if (sendBtn) {
        sendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleSend();
        });
    }

    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSend();
            }
        });
    }
}

/* Quick Question Pill Fill */
function fillChatInput(text) {
    const dedicatedInput = document.getElementById('chatInput');
    const dedicatedBtn = document.getElementById('sendBtn');
    const floatInput = document.getElementById('floatChatInput');
    const floatBtn = document.getElementById('sendFloatMsg');

    if (dedicatedInput) {
        dedicatedInput.value = text;
        dedicatedInput.focus();
        if (dedicatedBtn) dedicatedBtn.click();
    } else if (floatInput) {
        floatInput.value = text;
        const floatWin = document.getElementById('floatingChatWindow');
        if (floatWin) floatWin.classList.add('active');
        floatInput.focus();
        if (floatBtn) floatBtn.click();
    }
}

/* Prediction Form Submission */
function initPredictionForm() {
    const form = document.getElementById('predictionForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const payload = {};
        formData.forEach((val, key) => payload[key] = val);

        const submitBtn = form.querySelector('button[type="submit"]');
        const origText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '⚡ Processing Clinical Data...';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            submitBtn.disabled = false;
            submitBtn.innerHTML = origText;

            if (data.success) {
                renderPredictionResults(data);
            } else {
                alert('Prediction Error: ' + (data.error || 'Failed to process report'));
            }
        } catch (e) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = origText;
            alert('Server network error. Please ensure Flask app is running.');
        }
    });
}

function renderPredictionResults(data) {
    const modal = document.getElementById('predictionResultModal');
    const riskScore = document.getElementById('resRiskScore');
    const riskLevel = document.getElementById('resRiskLevel');
    const recsList = document.getElementById('resRecsList');

    if (riskScore) riskScore.innerText = `${data.risk_percentage}%`;
    if (riskLevel) {
        riskLevel.innerText = data.risk_level;
        riskLevel.className = 'badge-risk ';
        if (data.risk_percentage >= 60) riskLevel.classList.add('badge-high');
        else if (data.risk_percentage >= 30) riskLevel.classList.add('badge-moderate');
        else riskLevel.classList.add('badge-low');
    }

    if (recsList) {
        recsList.innerHTML = '';
        data.recommendations.forEach(r => {
            const li = document.createElement('li');
            li.style.marginBottom = '0.5rem';
            li.innerHTML = `• ${r}`;
            recsList.appendChild(li);
        });
    }

    if (modal) {
        modal.style.display = 'flex';
    } else {
        alert(`Prediction Complete!\nRisk Percentage: ${data.risk_percentage}%\nRisk Level: ${data.risk_level}`);
    }
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

/* Doctor Notes Handler */
function initDoctorNotes() {
    const noteForms = document.querySelectorAll('.doctor-note-form');
    noteForms.forEach(f => {
        f.addEventListener('submit', async (e) => {
            e.preventDefault();
            const recordId = f.dataset.recordId;
            const notes = f.querySelector('textarea').value;
            const btn = f.querySelector('button');

            btn.disabled = true;
            try {
                const res = await fetch('/api/doctor/notes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ record_id: recordId, notes: notes })
                });
                const data = await res.json();
                btn.disabled = false;
                if (data.success) {
                    alert('Doctor note saved successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                btn.disabled = false;
                alert('Server connection error.');
            }
        });
    });
}

/* Admin Role Handler */
function initAdminRoleEditor() {
    const roleSelects = document.querySelectorAll('.admin-role-select');
    roleSelects.forEach(sel => {
        sel.addEventListener('change', async (e) => {
            const userId = sel.dataset.userId;
            const newRole = sel.value;

            try {
                const res = await fetch('/api/admin/users/role', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, role: newRole })
                });
                const data = await res.json();
                if (data.success) {
                    alert(`User role updated to ${newRole}`);
                } else {
                    alert('Error updating role: ' + data.error);
                }
            } catch (err) {
                alert('Network error updating role.');
            }
        });
    });
}
