document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const inputText = document.getElementById('inputText');
    const inputWordCount = document.getElementById('inputWordCount');
    const inputSentenceCount = document.getElementById('inputSentenceCount');
    const compressionRange = document.getElementById('compressionRange');
    const compressionValue = document.getElementById('compressionValue');
    const btnSummarize = document.getElementById('btnSummarize');
    const btnClear = document.getElementById('btnClear');
    const alertBox = document.getElementById('alertBox');
    const alertMessage = document.getElementById('alertMessage');
    
    // Metrics
    const metricsBar = document.getElementById('metricsBar');
    const metricOrigWords = document.getElementById('metricOrigWords');
    const metricSummWords = document.getElementById('metricSummWords');
    const metricCompression = document.getElementById('metricCompression');
    const metricSentences = document.getElementById('metricSentences');
    
    // Tabs & Output
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const placeholderState = document.getElementById('placeholderState');
    const summaryResultState = document.getElementById('summaryResultState');
    const summaryText = document.getElementById('summaryText');
    const highlightContent = document.getElementById('highlightContent');
    const keywordsList = document.getElementById('keywordsList');
    const scoresTableBody = document.getElementById('scoresTableBody');
    
    // Action Buttons
    const btnCopy = document.getElementById('btnCopy');
    const btnDownload = document.getElementById('btnDownload');
    const btnSpeak = document.getElementById('btnSpeak');
    const btnPresets = document.querySelectorAll('.btn-preset');

    // Speech Synthesis
    let synth = window.speechSynthesis;
    let isSpeaking = false;

    // 1. Text Input Word & Sentence Count Updates
    function updateCounts() {
        const text = inputText.value.trim();
        if (!text) {
            inputWordCount.innerHTML = `<i class="fa-solid fa-font"></i> 0 words`;
            inputSentenceCount.innerHTML = `<i class="fa-solid fa-list-ol"></i> 0 sentences`;
            return;
        }
        
        // Count words
        const words = text.match(/\b\w+\b/g) || [];
        inputWordCount.innerHTML = `<i class="fa-solid fa-font"></i> ${words.length} words`;
        
        // Count sentences
        const sentences = text.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 0);
        inputSentenceCount.innerHTML = `<i class="fa-solid fa-list-ol"></i> ${sentences.length} sentences`;
    }

    inputText.addEventListener('input', updateCounts);

    // 2. Compression Slider Update
    compressionRange.addEventListener('input', (e) => {
        compressionValue.textContent = `${e.target.value}%`;
    });

    // 3. Clear Button Action
    btnClear.addEventListener('click', () => {
        inputText.value = '';
        updateCounts();
        hideAlert();
        resetResults();
    });

    // 4. Tab Navigation
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetTab = btn.getAttribute('data-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // 5. Preset Sample Loader
    btnPresets.forEach(btn => {
        btn.addEventListener('click', async () => {
            const sampleId = btn.getAttribute('data-sample');
            try {
                const response = await fetch(`/api/samples/${sampleId}`);
                const resData = await response.json();
                if (resData.success) {
                    inputText.value = resData.data.text;
                    updateCounts();
                    hideAlert();
                    // Trigger summarize automatically for seamless demo
                    handleSummarization();
                }
            } catch (err) {
                showAlert('Failed to load sample article.');
            }
        });
    });

    // 6. Summarize Action Handler
    btnSummarize.addEventListener('click', handleSummarization);

    async function handleSummarization() {
        const text = inputText.value.trim();
        const compression = compressionRange.value;

        if (!text) {
            showAlert('Please enter or paste an article into the text area.');
            return;
        }

        const words = text.match(/\b\w+\b/g) || [];
        if (words.length < 15) {
            showAlert(`Text is too short (${words.length} words). Minimum 15-20 words required for summarization.`);
            return;
        }

        hideAlert();
        setLoadingState(true);

        try {
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    compression: compression
                })
            });

            const data = await response.json();

            if (!data.success) {
                showAlert(data.error || 'Summarization failed.');
                setLoadingState(false);
                return;
            }

            // Display Results
            renderResults(data);

        } catch (error) {
            showAlert('Server connection error. Please make sure the Flask app is running.');
        } finally {
            setLoadingState(false);
        }
    }

    // 7. Render Results & Analytics
    function renderResults(data) {
        // Show Metrics Bar
        metricsBar.classList.remove('metrics-hidden');
        animateValue(metricOrigWords, 0, data.original_word_count, 400);
        animateValue(metricSummWords, 0, data.summary_word_count, 400);
        metricCompression.textContent = `${data.compression_ratio}%`;
        metricSentences.textContent = `${data.summary_sentence_count} / ${data.original_sentence_count}`;

        // Tab 1: Summary Output
        placeholderState.style.display = 'none';
        summaryResultState.classList.remove('result-hidden');
        summaryText.textContent = data.summary;

        // Tab 2: Highlighted Original Text
        if (data.sentences && data.selected_indices) {
            const selectedSet = new Set(data.selected_indices);
            const html = data.sentences.map((sent, idx) => {
                if (selectedSet.has(idx)) {
                    return `<span class="sentence-extract" title="Sentence #${idx+1} extracted">${sent}</span>`;
                } else {
                    return `<span class="sentence-normal">${sent}</span>`;
                }
            }).join(' ');
            highlightContent.innerHTML = html;
        }

        // Tab 3: Key Keywords Grid
        if (data.top_keywords && Object.keys(data.top_keywords).length > 0) {
            let tagsHtml = '';
            for (const [word, freq] of Object.entries(data.top_keywords)) {
                tagsHtml += `
                    <div class="keyword-tag">
                        <span>${word}</span>
                        <span class="keyword-freq">${freq}x</span>
                    </div>
                `;
            }
            keywordsList.innerHTML = tagsHtml;
        } else {
            keywordsList.innerHTML = `<span class="text-muted">No high-frequency keywords found.</span>`;
        }

        // Tab 4: Sentence Score Analytics Table
        if (data.sentence_scores && data.sentence_scores.length > 0) {
            const selectedSet = new Set(data.selected_indices || []);
            let tableRows = '';
            
            data.sentence_scores.forEach((item, index) => {
                const isSelected = selectedSet.has(item.index);
                const rowClass = isSelected ? 'selected-row' : '';
                const isExtractedBadge = isSelected ? `<span class="badge-count text-primary"><i class="fa-solid fa-check"></i> Extracted</span>` : '';
                
                tableRows += `
                    <tr class="${rowClass}">
                        <td><strong>S${item.index + 1}</strong></td>
                        <td>
                            ${item.sentence}
                            ${isExtractedBadge}
                        </td>
                        <td>${item.word_count}</td>
                        <td><span class="score-badge">${item.score}</span></td>
                    </tr>
                `;
            });
            scoresTableBody.innerHTML = tableRows;
        }
    }

    // Helper functions
    function setLoadingState(loading) {
        const btnText = btnSummarize.querySelector('.btn-text');
        const btnSpinner = btnSummarize.querySelector('.btn-spinner');
        
        if (loading) {
            btnSummarize.disabled = true;
            btnText.style.display = 'none';
            btnSpinner.classList.remove('spinner-hidden');
        } else {
            btnSummarize.disabled = false;
            btnText.style.display = 'inline-block';
            btnSpinner.classList.add('spinner-hidden');
        }
    }

    function showAlert(msg) {
        alertMessage.textContent = msg;
        alertBox.classList.remove('alert-hidden');
    }

    function hideAlert() {
        alertBox.classList.add('alert-hidden');
    }

    function resetResults() {
        metricsBar.classList.add('metrics-hidden');
        placeholderState.style.display = 'flex';
        summaryResultState.classList.add('result-hidden');
        summaryText.textContent = '';
        highlightContent.innerHTML = `<p class="text-muted">Generate a summary to view highlighted sentences in original article.</p>`;
        keywordsList.innerHTML = `<span class="text-muted">No keywords extracted yet.</span>`;
        scoresTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No sentence scores available.</td></tr>`;
    }

    function animateValue(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // 8. Copy Summary Button Action
    btnCopy.addEventListener('click', () => {
        const textToCopy = summaryText.textContent;
        if (!textToCopy) return;
        navigator.clipboard.writeText(textToCopy).then(() => {
            const origText = btnCopy.innerHTML;
            btnCopy.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
            setTimeout(() => { btnCopy.innerHTML = origText; }, 2000);
        });
    });

    // 9. Download Summary Button Action
    btnDownload.addEventListener('click', () => {
        const textToDownload = summaryText.textContent;
        if (!textToDownload) return;
        const blob = new Blob([textToDownload], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `summary_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // 10. Text to Speech Action
    btnSpeak.addEventListener('click', () => {
        if (!synth) {
            showAlert('Speech synthesis is not supported in your browser.');
            return;
        }
        
        if (isSpeaking) {
            synth.cancel();
            isSpeaking = false;
            btnSpeak.innerHTML = `<i class="fa-solid fa-volume-high"></i> Listen`;
            return;
        }

        const textToSpeak = summaryText.textContent;
        if (!textToSpeak) return;

        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.rate = 1.0;
        
        utterance.onend = () => {
            isSpeaking = false;
            btnSpeak.innerHTML = `<i class="fa-solid fa-volume-high"></i> Listen`;
        };

        utterance.onerror = () => {
            isSpeaking = false;
            btnSpeak.innerHTML = `<i class="fa-solid fa-volume-high"></i> Listen`;
        };

        synth.speak(utterance);
        isSpeaking = true;
        btnSpeak.innerHTML = `<i class="fa-solid fa-stop"></i> Stop`;
    });
});
