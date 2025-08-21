// Web Speech API STT, GPT translation via Flask, and Web Speech Synthesis TTS

// ======== Language options (STT+TTS) ========
const LANGS = [
  { label: "English (US)", code: "en-US" },
  { label: "English (UK)", code: "en-GB" },
  { label: "Hindi(Indian)", code: "hi-IN" },
  { label: "Spanish (Spain)", code: "es-ES" },
  { label: "Spanish (Mexico)", code: "es-MX" },
  { label: "German", code: "de-DE" },
  { label: "French", code: "fr-FR" },
  
];

// ======== DOM refs ========
const inputSel = document.getElementById("inputLang");
const outputSel = document.getElementById("outputLang");
const liveMode = document.getElementById("liveMode");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const translateBtn = document.getElementById("translateBtn");
const speakBtn = document.getElementById("speakBtn");

const originalBox = document.getElementById("original");
const translatedBox = document.getElementById("translated");

// Populate selects
for (const l of LANGS) {
  const o1 = document.createElement("option");
  o1.value = l.code; o1.textContent = l.label;
  inputSel.appendChild(o1);

  const o2 = document.createElement("option");
  o2.value = l.code; o2.textContent = l.label;
  outputSel.appendChild(o2);
}
inputSel.value = "ur-PK";
outputSel.value = "en-US";

// ======== STT (Web Speech API) ========
let recognition = null;
let isRecording = false;
let bufferText = ""; // accumulates final transcripts

function initRecognizer() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    alert("Web Speech API (SpeechRecognition) not supported in this browser. Try Chrome/Edge.");
    return null;
  }
  const rec = new SR();
  rec.continuous = true;          // keep listening
  rec.interimResults = true;      // show interim
  rec.maxAlternatives = 1;
  return rec;
}

function startRecording() {
  if (isRecording) return;
  recognition = initRecognizer();
  if (!recognition) return;

  bufferText = "";
  originalBox.textContent = "Listening…";
  translatedBox.textContent = "—";

  recognition.lang = inputSel.value;
  recognition.onresult = async (event) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const res = event.results[i];
      const txt = res[0].transcript;
      if (res.isFinal) {
        bufferText += (bufferText ? " " : "") + txt.trim();
        originalBox.textContent = bufferText;
        // Live mode: translate each final chunk
        if (liveMode.checked && txt.trim()) {
          const translated = await translateViaAPI(txt.trim(), inputSel.value, outputSel.value);
          // Append translation line by line
          const prev = translatedBox.textContent === "—" ? "" : translatedBox.textContent + " ";
          translatedBox.textContent = (prev + translated).trim();
        }
      } else {
        interim += txt;
      }
    }
    if (interim) {
      // show live interim
      originalBox.textContent = (bufferText ? bufferText + " " : "") + "(" + interim + ")";
    }
  };
  recognition.onerror = (e) => {
    console.error("STT error:", e.error);
  };
  recognition.onend = () => {
    // Auto-stop UI state; user can click start again
    isRecording = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
  };

  recognition.start();
  isRecording = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;
}

function stopRecording() {
  if (!recognition) return;
  try { recognition.stop(); } catch {}
  isRecording = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
}

// ======== Translation (Flask → OpenAI) ========
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

// Manual translate entire buffer
async function doTranslate() {
  const srcText = (originalBox.textContent || "").replace(/^—$/, "").trim();
  if (!srcText) return;
  const translated = await translateViaAPI(srcText, inputSel.value, outputSel.value);
  translatedBox.textContent = translated || "—";
}

// ======== TTS (Web Speech Synthesis) ========
function speak(text, langCode) {
  if (!("speechSynthesis" in window)) {
    alert("Speech Synthesis not supported in this browser.");
    return;
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = langCode;

  // Try to pick a voice matching the lang
  const pickVoice = () => {
    const voices = window.speechSynthesis.getVoices() || [];
    const match = voices.find(v => v.lang && (v.lang === langCode || v.lang.startsWith(langCode.split("-")[0])));
    if (match) utter.voice = match;
    window.speechSynthesis.cancel(); // stop prior
    window.speechSynthesis.speak(utter);
  };

  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = pickVoice;
  } else {
    pickVoice();
  }
}

// ======== Wire up ========
startBtn.addEventListener("click", startRecording);
stopBtn.addEventListener("click", stopRecording);
translateBtn.addEventListener("click", doTranslate);
speakBtn.addEventListener("click", () => {
  const text = (translatedBox.textContent || "").replace(/^—$/, "").trim();
  if (!text) return;
  speak(text, outputSel.value);
});
