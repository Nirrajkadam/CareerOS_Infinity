"""Authenticated conversational assistant and optional Indian neural speech."""
from html import escape
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.career_assistant import CareerAssistant, ChatRequest

router = APIRouter(prefix='/assistant', tags=['Career assistant'])
VOICES = {'en-IN': 'en-IN-NeerjaNeural', 'hi-IN': 'hi-IN-SwaraNeural'}


@router.get('/config')
async def assistant_config(user: User = Depends(get_current_user)):
    return {'ai_configured': bool(settings.GEMINI_API_KEY),
            'neural_voice_configured': bool(settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION),
            'languages': list(VOICES), 'voice_persona': 'Indian female'}


@router.post('/chat')
async def chat(payload: ChatRequest, user: User = Depends(get_current_user),
               session: AsyncSession = Depends(get_db_session)):
    return await CareerAssistant.run(payload, session, user)


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1800)
    language: Literal['en-IN', 'hi-IN'] = 'en-IN'


@router.post('/speech')
async def speech(payload: SpeechRequest, user: User = Depends(get_current_user)):
    if not settings.AZURE_SPEECH_KEY or not settings.AZURE_SPEECH_REGION:
        raise HTTPException(503, 'Neural speech is not configured. Use a device voice.')
    ssml = (f'<speak version="1.0" xml:lang="{payload.language}">'
            f'<voice name="{VOICES[payload.language]}">{escape(payload.text)}</voice></speak>')
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            result = await client.post(
                f'https://{settings.AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1',
                headers={'Ocp-Apim-Subscription-Key': settings.AZURE_SPEECH_KEY,
                         'Content-Type': 'application/ssml+xml',
                         'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
                         'User-Agent': 'CareerOS'}, content=ssml.encode('utf-8'))
            result.raise_for_status()
            if not result.content or not result.headers.get('content-type', '').startswith('audio/'):
                raise ValueError('No speech audio returned')
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'Neural speech is unavailable. Use a device voice.')
    return Response(result.content, media_type='audio/mpeg', headers={'Cache-Control': 'no-store'})
