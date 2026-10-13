"""Gera o MP3 do Radar usando a API REST do Voicebox (github.com/jamiepine/voicebox).

Alternativa à seção 7D: mesmo contrato de entrada e saída.
Uso: python radar_audio_voicebox.py <saida.mp3> [radar.json]
Requer um servidor Voicebox rodando (VOICEBOX_URL, padrão http://127.0.0.1:17493).
Variáveis opcionais: VOICEBOX_PROFILE (nome do perfil, padrão "Dora Radar"),
VOICEBOX_ENGINE (padrão kokoro), VOICEBOX_VOICE (padrão pf_dora) e
VOICEBOX_MODEL_SIZE (ex.: 0.6B para o Qwen3-TTS).
"""
import io, json, os, sys, time, urllib.request
import numpy as np, soundfile as sf, lameenc

BASE = os.environ.get('VOICEBOX_URL', 'http://127.0.0.1:17493').rstrip('/')
PROFILE = os.environ.get('VOICEBOX_PROFILE', 'Dora Radar')
ENGINE = os.environ.get('VOICEBOX_ENGINE', 'kokoro')
VOICE = os.environ.get('VOICEBOX_VOICE', 'pf_dora')


def call(method, path, payload=None, raw=False):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={'Content-Type': 'application/json'})
    body = urllib.request.urlopen(req, timeout=600).read()
    return body if raw else json.loads(body)


def profile_id():
    for p in call('GET', '/profiles'):
        if p['name'].lower() == PROFILE.lower():
            return p['id']
    return call('POST', '/profiles', {'name': PROFILE, 'language': 'pt', 'voice_type': 'preset',
                                      'preset_engine': ENGINE, 'preset_voice_id': VOICE, 'default_engine': ENGINE})['id']


def speak(pid, text):
    req = {'profile_id': pid, 'text': text, 'language': 'pt', 'engine': ENGINE}
    if os.environ.get('VOICEBOX_MODEL_SIZE'):
        req['model_size'] = os.environ['VOICEBOX_MODEL_SIZE']
    g = call('POST', '/generate', req)
    while True:
        h = call('GET', '/history/' + g['id'])
        if h['status'] == 'completed':
            break
        if h['status'] == 'failed':
            raise RuntimeError(h.get('error') or 'falha na geração')
        time.sleep(1)
    audio, sr = sf.read(io.BytesIO(call('GET', '/audio/' + g['id'], raw=True)), dtype='float32')
    return (audio.mean(axis=1) if audio.ndim > 1 else audio), sr


d = json.load(open(sys.argv[2] if len(sys.argv) > 2 else '/tmp/radar.json', encoding='utf-8'))
pid = profile_id()
parts, sr = [], 24000
for s in d['slides']:
    t = (s.get('fala') or (s.get('titulo', '') + '. ' + s.get('texto', ''))).strip()
    if not t:
        continue
    a, sr = speak(pid, t)
    parts += [a, np.zeros(int(sr * 0.7), dtype=np.float32)]
audio = np.concatenate(parts)
pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes()
enc = lameenc.Encoder()
enc.set_bit_rate(48); enc.set_in_sample_rate(sr); enc.set_channels(1); enc.set_quality(2)
mp3 = enc.encode(pcm) + enc.flush()
open(sys.argv[1], 'wb').write(mp3)
print('duracao_s=%.0f bytes=%d' % (len(audio) / sr, len(mp3)))
