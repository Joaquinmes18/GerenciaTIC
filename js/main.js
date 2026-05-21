tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                background: '#030712',
                surface: '#111827',
                primary: '#3b82f6',
                secondary: '#6366f1',
                accent: '#10b981',
                alert: '#ef4444',
            }
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const feedbackForm = document.querySelector('#feedback form');

    if (!feedbackForm) {
        return;
    }

    const submitButton = feedbackForm.querySelector('button[type="submit"]');
    const originalButtonText = submitButton ? submitButton.textContent.trim() : '';

    feedbackForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(feedbackForm);
        const payload = {
            nombre: String(formData.get('nombre') || '').trim(),
            email: String(formData.get('email') || '').trim(),
            sugerencia: String(formData.get('sugerencia') || '').trim(),
            funcion: String(formData.get('funcion') || '').trim(),
        };

        if (!payload.nombre || !payload.email || !payload.sugerencia || !payload.funcion) {
            window.alert('Completa todos los campos antes de enviar.');
            return;
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Enviando...';
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error('No fue posible guardar el feedback.');
            }

            feedbackForm.reset();
            window.alert('Gracias. Tu sugerencia fue guardada.');
        } catch (error) {
            const pendingFeedback = JSON.parse(localStorage.getItem('phishshield-feedback-pending') || '[]');
            pendingFeedback.push({
                ...payload,
                created_at: new Date().toISOString(),
            });
            localStorage.setItem('phishshield-feedback-pending', JSON.stringify(pendingFeedback));
            feedbackForm.reset();
            window.alert('No se pudo conectar con el backend. Tu sugerencia quedó guardada localmente para enviarla luego.');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText || 'Enviar feedback';
            }
        }
    });
});