# KAI voice and task assistant

Open **Ask KAI** after signing in. Type an instruction or tap the microphone, speak, and pause. KAI uses the completed transcript, keeps conversation context for the current tab, and reports the steps it actually completed. Cancel listening discards that recording. Close, Stop voice and disabling Read replies aloud stop playback.

Choose **English (India)** or **Hindi**. The optional neural voice is female: Neerja for Indian English and Swara for Hindi. Without neural speech configuration, KAI selects an available Indian device voice, then a voice in the same language. Device voice quality, gender and availability depend on the browser/OS. Voice input uses the browser's speech service and needs microphone permission and HTTPS (or localhost).

## Automatic tasks

With Gemini configured, examples include:

- “Search DevOps jobs in Pune, compare my profile and prepare the best one.”
- “Read my resume and explain the skills missing for these jobs.”
- “Show my applications and tell me what to work on next.”
- “मेरा प्रोफाइल देखो और मेरी स्किल्स बताओ।”

The assistant can read your profile/current master resume, search stored active jobs, compute indicative matches, prepare application records, list your applications and open supported pages. It chooses the necessary tools automatically within one request. It performs at most eight tool calls and prepares at most three records per request, with a 110-second task deadline. Duplicate requests reuse an existing application record for the same user/job. Successful steps commit individually, so their results remain available if the model later fails.

Search covers records already in CareerOS, not a live search of every portal. The existing matching engine provides heuristic scores. Preparing a record does not submit it to an employer. Sending emails, external portal submissions, desktop control, arbitrary code execution and unattended background operation are not exposed as assistant tools.

## Server configuration

Set these on the backend (never in frontend code):

```dotenv
GEMINI_API_KEY=your-private-provider-key
ASSISTANT_MODEL=gemini/gemini-3.5-flash
# Optional Azure Speech resource for neural speech:
AZURE_SPEECH_KEY=your-private-speech-resource-key
AZURE_SPEECH_REGION=centralindia
```

Use the actual region of your Azure Speech resource. Select a Gemini model available to your account that supports function calling. Restart the backend after changing configuration. No paid provider account or deployment is created by this change.

Without a Gemini key, exact basic commands remain available: “Show my profile”, “Show my resume”, “Show my applications”, “Search Python jobs”, and “Open resume”. The interface labels this limited mode. It does not pretend that a missing or failing model has executed a task.

Every API route requires an authenticated active account. Tool arguments cannot select another user; identity comes from the session. The legacy `/jobpilot/agent-command` route delegates to the same restricted task runner. Shared desktop and inbox operations remain outside it. Provider credentials stay on the server; speech text is escaped as SSML, and returned audio is marked no-store.

## Verification

Focused tests cover authentication, ordinary-account access, input validation, tool budgets, duplicate tool execution, failure reporting, identity override rejection, voice selection, final transcript assembly, navigation restrictions and the Azure request contract. A database integration test exercises search, profile read, matching, record preparation and application ownership. Live provider audio quality and microphone recognition accuracy require testing on a configured deployment and the user's device.

Provider references:
- [Azure speech REST API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech)
- [Azure voice availability](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts)
- [LiteLLM function calling](https://docs.litellm.ai/docs/completion/function_call)
- [Browser speech recognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)
