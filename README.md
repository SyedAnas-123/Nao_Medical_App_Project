
# Healthcare Translation Web App


A demo web application that converts speech into text, translates it into a selected language, and plays back the translated text as audio.  

This project was built as part of a prototype demonstration for multilingual communication using **Speech-to-Text (STT)**, **Machine Translation(GenAI)**, and **Text-to-Speech (TTS)**.



## Features

- 🎤 **Record Audio**: Capture user speech directly from the browser.  
- ✍️ **Speech-to-Text (STT)**: Convert audio to text using an ASR model.  
- 🌍 **Translation**: Translate recognized text into different languages (e.g., English, Spanish, French).  
- 🔊 **Text-to-Speech (TTS)**: Play back translated text as audio.  
- 📱 **Responsive Design**: Works seamlessly on both desktop and mobile devices.  



## Tech Stack

- **Frontend**: HTML, CSS (responsive design), JavaScript (fetch API).  
- **Backend**: Flask (Python).  
- **AI Models/Services**:  
  - Automatic Speech Recognition (ASR)  
  - Machine Translation (LLM-based- GenAI)  
  - Text-to-Speech (TTS)  


## Project Structure
Nao Medical Project |

│── static/ # CSS, JS files

│── templates/ # HTML files

│── app.py # Flask backend

│── requirements.txt # Python dependencies

│── .env # Secret keys (hidden)

│── README.md # Project description
## API Reference

#### Speech-to-Text API

```http
  POST /api/speech-to-text
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Authentication key
  `audio`   | `file`   | **Required**. Audio input from user’s microphone

#### Translation API (GPT) API

```http
POST /api/translate
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `text`      | `string` | **Required**. Text to be translated |

#### Text-to-Speech (TTS) API

```http
POST /api/text-to-speech
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `text`      | `string` | **Required**. Translated text to be spoken |


## Supported Languages
English ✅

Spanish ✅

French ✅

Hindi ✅

German ✅

## Environment Variables

API keys are stored in .env file.

.env is ignored using .gitignore.

Never push sensitive data to GitHub.


## 🚀 About Me
Developed by: Syed Anas

For: Hiring Prototype Submission

GitHub: https://github.com/SyedAnas-123


## Deployment

To deploy this project run

```bash
 pip install -r requirements.txt
 python app.py
```


## License

[MIT](https://choosealicense.com/licenses/mit/)

