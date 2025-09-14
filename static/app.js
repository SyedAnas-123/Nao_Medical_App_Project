// ================== Web Speech Translator ==================
// Handles: 
// - Speech-to-Text (STT) via Web Speech API
// - Translation via Flask backend (OpenAI GPT)
// - Text-to-Speech (TTS) playback

// ======== Language options (STT + TTS) ========
const LANGS = [
  { label: "English (US)", code: "en-US" },
  { label: "English (UK)", code: "en-GB" },
  { label: "Hindi (India)", code: "hi-IN" },
  { label: "Spanish (Spain)", code: "es-ES" },
  { label: "Spanish (Mexico)", code: "es-MX" },
  { label: "German", code: "de-DE" },
  { label: "French", code: "fr-FR" },
];

// ======== DOM references ========
const inputSel = document.getElementById("inputLang");   // Input language selector
const outputSel = document.getElementById("outputLang"); // Output language selector
const liveMode = document.getElementById("liveMode");    // Checkbox for live translation
const startBtn = document.getElementById("startBtn");    // Start recording
const stopBtn = document.getElementById("stopBtn");      // Stop recording
const translateBtn = document.getElementById("translateBtn"); // Manual translate button
const speakBtn = document.getElementById("speakBtn");    // Speak translated text

const originalBox = document.getElementById("original");     // Original text box
const translatedBox = document.getElementById("translated"); // Translated text box

// ======== Populate language dropdowns ========
for (const l of LANGS) {
  const o1 = document.createElement("option");
  o1.value = l.code; 
  o1.textContent = l.label;
  inputSel.appendChild(o1);

  const o2 = document.createElement("option");
  o2.value = l.code; 
  o2.textContent = l.label;
  outputSel.appendChild(o2);
}
// Default values
inputSel.value = "ur-PK";
outputSel.value = "en-US";

// ======== STT (Speech-to-Text) ========
let recognition = null;   // SpeechRecognition instance
let isRecording = false;  // Flag for recording state
let bufferText = "";      // Holds accumulated speech text

// Initialize speech recognizer
function initRecognizer() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    alert("Web Speech API not supported. Use Chrome/Edge.");
    return null;
  }
  const rec = new SR();
  rec.continuous = true;     // Keep listening until stopped
  rec.interimResults = true; // Show partial results
  rec.maxAlternatives = 1;
  return rec;
}

// Start recording voice
function startRecording() {
  if (isRecording) return;
  recognition = initRecognizer();
  if (!recognition) return;

  bufferText = "";
  originalBox.textContent = "Listening…";
  translatedBox.textContent = "—";

  // Set input language
  recognition.lang = inputSel.value;

  // Handle STT results
  recognition.onresult = async (event) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const res = event.results[i];
      const txt = res[0].transcript;
      
      if (res.isFinal) {
        // Final text → append to buffer
        bufferText += (bufferText ? " " : "") + txt.trim();
        originalBox.textContent = bufferText;

        // Live mode translation (chunk-by-chunk)
        if (liveMode.checked && txt.trim()) {
          const translated = await translateViaAPI(txt.trim(), inputSel.value, outputSel.value);
          const prev = translatedBox.textContent === "—" ? "" : translatedBox.textContent + " ";
          translatedBox.textContent = (prev + translated).trim();
        }
      } else {
        // Interim (not final yet)
        interim += txt;
      }
    }
    if (interim) {
      // Show interim text in parentheses
      originalBox.textContent = (bufferText ? bufferText + " " : "") + "(" + interim + ")";
    }
  };

  // Handle errors
  recognition.onerror = (e) => {
    console.error("STT error:", e.error);
  };

  // Handle auto-stop
  recognition.onend = () => {
    isRecording = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
  };

  recognition.start();
  isRecording = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;
}

// Stop recording voice
function stopRecording() {
  if (!recognition) return;
  try { recognition.stop(); } catch {}
  isRecording = false;
  startBtn.disabled = false;
  stopBtn.disabled = true ;
}

// ======== Translation (Flask API → OpenAI GPT) ========
async function translateViaAPI(text, fromLang, toLang) {
  const res = await fetch("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, from_lang: fromLang, to_lang: toLang }),
  });
  const data = await res.json();
  if (data.error) {
    alert("Translate error: " + data.error);
    return "";
  }
  return data.translated || "";
}

// Manual translation (for full text at once)
async function doTranslate() {
  const srcText = (originalBox.textContent || "").replace(/^—$/, "").trim();
  if (!srcText) return;
  const translated = await translateViaAPI(srcText, inputSel.value, outputSel.value);
  translatedBox.textContent = translated || "—";
}

// ======== TTS (Text-to-Speech) ========
function speak(text, langCode) {
  if (!("speechSynthesis" in window)) {
    alert("Speech Synthesis not supported.");
    return;
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = langCode;

  // Select a matching voice
  const pickVoice = () => {
    const voices = window.speechSynthesis.getVoices() || [];
    const match = voices.find(v => v.lang && (v.lang === langCode || v.lang.startsWith(langCode.split("-")[0])));
    if (match) utter.voice = match;
    window.speechSynthesis.cancel(); // Stop any previous speech
    window.speechSynthesis.speak(utter);
  };

  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = pickVoice;
  } else {
    pickVoice();
  }
}

// ======== Hook up buttons ========
startBtn.addEventListener("click", startRecording);
stopBtn.addEventListener("click", stopRecording);
translateBtn.addEventListener("click", doTranslate);
speakBtn.addEventListener("click", () => {
  const text = (translatedBox.textContent || "").replace(/^—$/, "").trim();
  if (!text) return;
  speak(text, outputSel.value);
});
