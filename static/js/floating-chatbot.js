// DreamFrame AI Bot Widget - Enhanced with Voice Output
document.addEventListener('DOMContentLoaded', function() {
    // DreamFrame AI Bot Widget Initialization
    const chatWidget = document.createElement('div');
    chatWidget.innerHTML = `
        <style>
            :root { --df-bg:#0b0f14; --df-panel:#121821; --df-accent:#6ac8ff; --df-text:#eef6ff; --df-muted:#9fb3c8; }
            .df-chat{position:fixed; right:20px; bottom:200px; width:380px; max-width:92vw; border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,.45); overflow:hidden; border:1px solid rgba(255,255,255,.08); background:linear-gradient(180deg,rgba(18,24,33,.98), rgba(18,24,33,.92)); backdrop-filter: blur(8px); z-index: 11000; display: none; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;}    
            .df-header{display:flex; align-items:center; gap:10px; padding:12px 14px; border-bottom:1px solid rgba(255,255,255,.06)}
            .df-star{width:18px; height:18px; border-radius:50%; background: radial-gradient(circle at 30% 30%, #fff, #9ed8ff 45%, transparent 60%); box-shadow:0 0 12px #9ed8ff}
            .df-title{font-weight:700; letter-spacing:.3px; color: var(--df-text);}
            .df-sub{font-size:12px; color:var(--df-muted)}
            .df-voice-controls{display:flex; gap:6px; align-items:center; margin-left:auto;}
            .df-voice-toggle{background:#0e2435; border:1px solid rgba(255,255,255,.08); color:var(--df-text); padding:4px 8px; border-radius:6px; cursor:pointer; font-size:11px; display:flex; align-items:center; gap:4px;}
            .df-voice-toggle.active{background:#1a4f2a; border-color:#4ade80;}
            .df-voice-select{background:#0e2435; border:1px solid rgba(255,255,255,.08); color:var(--df-text); padding:2px 6px; border-radius:4px; font-size:10px;}
            .df-log{height:380px; overflow:auto; padding:14px; display:flex; flex-direction:column; gap:10px}
            .df-msg{display:flex; gap:8px; align-items:flex-start}
            .df-msg.me{flex-direction: row-reverse}
            .df-msg .avatar{flex:0 0 28px; height:28px; border-radius:50%; background:#243144; display:grid; place-items:center; font-size:12px; color:#bfe6ff}
            .df-bubble{max-width:78%; padding:10px 12px; border-radius:12px; line-height:1.35; color: var(--df-text); position:relative;}
            .me .df-bubble{background:#243144}
            .bot .df-bubble{background:#0e2435; border:1px solid rgba(255,255,255,.06)}
            .df-audio-control{position:absolute; bottom:-2px; right:-2px; width:20px; height:20px; background:#ff6b35; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; font-size:10px; color:white; box-shadow:0 2px 6px rgba(0,0,0,.3);}
            .df-audio-control:hover{background:#f7931e;}
            .df-audio-control.playing{animation: df-pulse 1.5s infinite;}
            @keyframes df-pulse{0%,100%{transform:scale(1)} 50%{transform:scale(1.1)}}
            .df-meta{font-size:11px; color:var(--df-muted); margin-top:4px}
            .df-input{border-top:1px solid rgba(255,255,255,.06); padding:10px; display:flex; gap:8px; align-items:center}
            .df-input input[type="text"]{flex:1; padding:10px 12px; border-radius:10px; border:1px solid rgba(255,255,255,.08); background:#0c131c; color:var(--df-text)}
            .df-input input[type="file"]{display:none}
            .df-btn{border:1px solid rgba(255,255,255,.12); background:#0c131c; color:var(--df-text); padding:9px 12px; border-radius:10px; cursor:pointer; border: none; font-size:12px;}
            .df-btn:disabled{opacity:.6; cursor:not-allowed}
            .df-pill{padding:4px 8px; border-radius:999px; font-size:11px; border:1px dashed rgba(255,255,255,.2); color:var(--df-muted)}
            .df-typing{display:inline-block; width:6px; height:6px; margin-left:3px; border-radius:50%; background:var(--df-muted); animation: df-blink 1s infinite}
            .df-typing:nth-child(2){animation-delay:.2s}
            .df-typing:nth-child(3){animation-delay:.4s}
            @keyframes df-blink{0%,80%,100%{opacity:.2} 40%{opacity:1}}
            .df-hint{font-size:11px; color:var(--df-muted); padding:8px 14px; border-top:1px dashed rgba(255,255,255,.1)}
            .df-toggle-btn{position:fixed; bottom:200px; right:20px; width:60px; height:60px; background:linear-gradient(135deg, #ff6b35, #f7931e); border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:11001; color:white; font-size:1.5em; box-shadow:0 4px 20px rgba(0,0,0,.3); transition:all .3s ease; border:none;}
            .df-toggle-btn:hover{transform:translateY(-2px); box-shadow:0 6px 25px rgba(255,107,53,.4)}
            .df-close-btn{background:none; border:none; color:var(--df-text); cursor:pointer; font-size:16px;}
            .df-close-btn:hover{color:#fff;}
        </style>
        
        <button class="df-toggle-btn" id="df-toggle" aria-label="Open AI Chat">💬</button>
        
        <div class="df-chat" id="df-widget" role="dialog" aria-label="DreamFrame AI Chat">
            <div class="df-header">
                <div class="df-star" aria-hidden="true"></div>
                <div style="flex: 1;">
                    <div class="df-title">DreamFrame AI Bot</div>
                    <div class="df-sub">AI conversation with voice support</div>
                </div>
                <div class="df-voice-controls">
                    <button class="df-voice-toggle" id="df-voice-toggle" title="Toggle voice responses">
                        🔊 <span id="df-voice-status">Off</span>
                    </button>
                    <select class="df-voice-select" id="df-voice-select" title="Select voice">
                        <option value="alloy">Alloy</option>
                        <option value="echo">Echo</option>
                        <option value="fable">Fable</option>
                        <option value="onyx">Onyx</option>
                        <option value="nova">Nova</option>
                        <option value="shimmer">Shimmer</option>
                    </select>
                </div>
                <button class="df-close-btn" id="df-close">✕</button>
            </div>

            <div class="df-log" id="df-log" aria-live="polite">
                <div class="df-msg bot">
                    <div class="avatar">AI</div>
                    <div>
                        <div class="df-bubble">🎬 Welcome to DreamFrame AI! I can help you with video production, pricing, technical questions, and more. What would you like to know?</div>
                    </div>
                </div>
            </div>

            <div class="df-hint">Voice responses: <span id="df-voice-hint">Click 🔊 to enable voice output</span> • Voice input: Attach audio files</div>

            <div class="df-input">
                <label class="df-btn" for="df-voice">+ Voice</label>
                <input id="df-voice" type="file" accept="audio/*" />
                <input id="df-text" type="text" placeholder="Type a message… (Shift+Enter for newline)" />
                <button class="df-btn" id="df-send">Send</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(chatWidget);

    // Initialize chat functionality
    initDreamFrameChat();
});

function initDreamFrameChat() {
    const API_URL = "/api/ai-bot";
    const VOICE_API_URL = "/api/ai-bot/voice";
    const SESSION_ID_KEY = "df_session_id";
    const VOICE_ENABLED_KEY = "df_voice_enabled";
    const VOICE_SELECTION_KEY = "df_voice_selection";
    
    // Voice state
    let voiceEnabled = localStorage.getItem(VOICE_ENABLED_KEY) === 'true';
    let voiceSelection = localStorage.getItem(VOICE_SELECTION_KEY) || 'alloy';
    let currentAudio = null;
    
    function getSessionId(){
        try{
            let id = localStorage.getItem(SESSION_ID_KEY);
            if(!id){ 
                id = (crypto?.randomUUID?.() || String(Date.now())+Math.random()); 
                localStorage.setItem(SESSION_ID_KEY, id); 
            }
            return id;
        }catch{ return "anon" }
    }

    const logEl = document.getElementById('df-log');
    const textEl = document.getElementById('df-text');
    const voiceEl = document.getElementById('df-voice');
    const sendBtn = document.getElementById('df-send');
    const toggleBtn = document.getElementById('df-toggle');
    const closeBtn = document.getElementById('df-close');
    const widgetEl = document.getElementById('df-widget');
    const voiceToggleBtn = document.getElementById('df-voice-toggle');
    const voiceStatusEl = document.getElementById('df-voice-status');
    const voiceSelectEl = document.getElementById('df-voice-select');
    const voiceHintEl = document.getElementById('df-voice-hint');

    // Initialize voice UI
    updateVoiceUI();
    voiceSelectEl.value = voiceSelection;

    function updateVoiceUI() {
        if (voiceEnabled) {
            voiceToggleBtn.classList.add('active');
            voiceStatusEl.textContent = 'On';
            voiceHintEl.textContent = `Voice enabled (${voiceSelection}) • Click audio controls to replay`;
        } else {
            voiceToggleBtn.classList.remove('active');
            voiceStatusEl.textContent = 'Off';
            voiceHintEl.textContent = 'Click 🔊 to enable voice output';
        }
    }

    function el(html){ 
        const d = document.createElement('div'); 
        d.innerHTML = html.trim(); 
        return d.firstChild; 
    }
    
    function scrollToBottom(){ 
        logEl.scrollTop = logEl.scrollHeight; 
    }

    function escapeHtml(str){
        return str.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[m]));
    }

    function addMessage({role, content, meta, hasAudio = false}){
        const who = role === 'user' ? 'me' : 'bot';
        const avatar = who === 'me' ? 'ME' : 'AI';
        const audioControl = hasAudio ? `<div class="df-audio-control" data-message-audio="true" title="Play/pause voice">🔊</div>` : '';
        const node = el(`
            <div class="df-msg ${who}">
                <div class="avatar">${avatar}</div>
                <div>
                    <div class="df-bubble">
                        ${content}
                        ${audioControl}
                    </div>
                    ${meta ? `<div class="df-meta">${meta}</div>` : ''}
                </div>
            </div>
        `);
        logEl.appendChild(node); 
        scrollToBottom();
        return node;
    }

    async function playAudioForMessage(messageNode, text) {
        if (!voiceEnabled || !text) return;
        
        const audioControl = messageNode.querySelector('.df-audio-control');
        if (!audioControl) return;
        
        try {
            // INSTANT FEEDBACK - Start immediately
            audioControl.classList.add('playing');
            audioControl.title = "⚡ Ultra-Fast Voice Generation...";
            audioControl.textContent = "⚡"; // Visual indicator of speed
            
            // Optimize text for ULTRA-FAST TTS - super aggressive cleaning (matching backend)
            let optimizedText = text.replace(/<[^>]*>/g, '').replace(/[🎬🎯🚀💻🤖🛡️📈🎯✅⚡🏁📊🎵🍎🔍🟢🔑💬🎉🎨🎪🎭🎬🎯🚁🚀💡🔧🎤📱💰🏆⭐✨]/g, '').replace(/\$\d+[\+\-]?/g, '').replace(/\(\$.*?\)/g, '').trim();
            
            // SUPER AGGRESSIVE length limit (300 chars max for instant voice)
            if (optimizedText.length > 300) {
                // Use first sentence or truncate aggressively for speed
                const truncated = optimizedText.substring(0, 300);
                const firstPeriod = truncated.indexOf('.');
                if (firstPeriod > 100) {
                    optimizedText = truncated.substring(0, firstPeriod + 1);
                } else {
                    const firstComma = truncated.indexOf(',');
                    if (firstComma > 80) {
                        optimizedText = truncated.substring(0, firstComma) + '.';
                    } else {
                        optimizedText = truncated.split(' ').slice(0, -1).join(' ') + '.';
                    }
                }
            }
            
            const response = await fetch(VOICE_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: optimizedText, voice: voiceSelection })
            });
            
            if (!response.ok) {
                throw new Error(`Voice generation failed: ${response.status}`);
            }
            
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            // Store current audio and add event listeners
            if (currentAudio) {
                currentAudio.pause();
                currentAudio.removeEventListener('ended', currentAudio._cleanupFn);
            }
            currentAudio = audio;
            
            audio._cleanupFn = () => {
                audioControl.classList.remove('playing');
                audioControl.title = "Replay voice";
                URL.revokeObjectURL(audioUrl);
            };
            
            audio.addEventListener('ended', audio._cleanupFn);
            audio.addEventListener('error', audio._cleanupFn);
            
            // Set up click handler for replay
            audioControl.onclick = () => {
                if (audio.paused) {
                    if (currentAudio && currentAudio !== audio) {
                        currentAudio.pause();
                    }
                    currentAudio = audio;
                    audioControl.classList.add('playing');
                    audio.currentTime = 0;
                    audio.play();
                } else {
                    audio.pause();
                    audioControl.classList.remove('playing');
                }
            };
            
            audioControl.title = "Playing voice...";
            await audio.play();
            
        } catch (error) {
            console.warn('Voice playback failed:', error);
            audioControl.classList.remove('playing');
            audioControl.title = "Voice unavailable";
            audioControl.style.background = '#dc2626';
        }
    }

    let typingNode = null;
    function showTyping(){
        if(typingNode) return;
        typingNode = addMessage({
            role:'assistant', 
            content:`<span class="df-typing"></span><span class="df-typing"></span><span class="df-typing"></span>`, 
            meta:"Thinking…"
        });
    }
    
    function hideTyping(){ 
        if(!typingNode) return; 
        typingNode.remove(); 
        typingNode = null; 
    }

    async function sendMessage(){
        const text = textEl.value.trim();
        const file = voiceEl.files && voiceEl.files[0];
        if(!text && !file){ textEl.focus(); return; }

        sendBtn.disabled = true;

        if(text){ addMessage({role:'user', content: escapeHtml(text)}); }
        if(file){ addMessage({role:'user', content: `🎤 Voice note attached: <span class="df-pill">${escapeHtml(file.name)}</span>`}); }
        textEl.value = '';
        voiceEl.value = '';

        showTyping();

        try{
            let headers = { 'X-DF-Session': getSessionId() };
            let res;

            if(file){
                const fd = new FormData();
                if(text) fd.append('text', text);
                fd.append('audio', file, file.name);
                res = await fetch(API_URL, { method:'POST', headers, body: fd });
            } else {
                res = await fetch(API_URL, { 
                    method:'POST', 
                    headers: { ...headers, 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ text }) 
                });
            }

            if(!res.ok){ throw new Error(`HTTP ${res.status}`); }
            const data = await res.json();
            hideTyping();
            
            const messageNode = addMessage({
                role:'assistant', 
                content: data.message || 'Done.', 
                meta: data.meta || '',
                hasAudio: voiceEnabled
            });
            
            // Start voice generation immediately if enabled
            if (voiceEnabled && data.message) {
                // Start voice generation immediately - no delay
                playAudioForMessage(messageNode, data.message).catch(console.warn);
            }
            
        } catch(err){
            hideTyping();
            addMessage({
                role:'assistant', 
                content:`⚠️ <b>Sorry, something went wrong.</b><br><small>${escapeHtml(err.message)}</small>`
            });
        } finally {
            sendBtn.disabled = false;
        }
    }

    // Event listeners
    toggleBtn.addEventListener('click', () => {
        // Properly check if widget is visible - handle empty string as hidden
        const isVisible = widgetEl.style.display === 'block';
        widgetEl.style.display = isVisible ? 'none' : 'block';
    });

    closeBtn.addEventListener('click', () => {
        widgetEl.style.display = 'none';
        if (currentAudio) {
            currentAudio.pause();
        }
    });

    voiceToggleBtn.addEventListener('click', () => {
        voiceEnabled = !voiceEnabled;
        localStorage.setItem(VOICE_ENABLED_KEY, voiceEnabled);
        updateVoiceUI();
        
        if (!voiceEnabled && currentAudio) {
            currentAudio.pause();
        }
    });

    voiceSelectEl.addEventListener('change', () => {
        voiceSelection = voiceSelectEl.value;
        localStorage.setItem(VOICE_SELECTION_KEY, voiceSelection);
        updateVoiceUI();
    });

    textEl.addEventListener('keydown', (e) => {
        if(e.key === 'Enter' && !e.shiftKey){ 
            e.preventDefault(); 
            sendMessage(); 
        }
    });
    
    sendBtn.addEventListener('click', sendMessage);
}