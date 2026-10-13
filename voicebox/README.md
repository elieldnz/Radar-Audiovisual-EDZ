# Teste: Voicebox no Radar Audiovisual EDZ

[Voicebox](https://github.com/jamiepine/voicebox) é um estúdio de voz com IA, open source (MIT), que roda localmente e expõe uma API REST (`http://127.0.0.1:17493`). Este teste usa essa API para narrar o podcast do Radar, no lugar do `kokoro-onnx` da seção 7D.

## Resultado do teste (13/10/2026, container em nuvem, só CPU, 4 núcleos)

- Servidor do Voicebox (backend FastAPI, `python -m backend.main`) subiu em modo CPU.
- Perfil `Dora Radar` criado com a voz pré-definida `pf_dora` do motor Kokoro (a mesma voz usada hoje).
- `exemplo_radar.json` (4 stories, conteúdo de teste) virou `Radar-EDZ-Teste-Voicebox.mp3`: **40 s de áudio gerados em cerca de 19 s**, 48 kbps mono, pico em -1,4 dB.

## Como rodar

```
git clone https://github.com/jamiepine/voicebox.git && cd voicebox
uv venv -p 3.12 .venv && VIRTUAL_ENV=.venv uv pip install -r backend/requirements.txt lameenc
.venv/bin/python -m backend.main --host 127.0.0.1 --port 17493 &
.venv/bin/python /caminho/radar_audio_voicebox.py /tmp/Radar-EDZ-Manha-DD-MM.mp3 /tmp/radar.json
```

O script cria o perfil se ele não existir e imprime `duracao_s=... bytes=...`, igual ao script da seção 7D. Variáveis opcionais: `VOICEBOX_URL`, `VOICEBOX_PROFILE`, `VOICEBOX_ENGINE`, `VOICEBOX_VOICE`.

## Observações

- **Python 3.12**: o pacote `kokoro` exigido pelo Voicebox não instala no Python 3.13.
- **Rede**: o Voicebox baixa os modelos do Hugging Face. No ambiente deste teste o `huggingface.co` estava bloqueado; os pesos do Kokoro (`kokoro-v1_0.pth`, `config.json`) e a voz `pf_dora.pt` vieram de espelhos no GitHub (releases do `remsky/Kokoro-FastAPI`) e foram colocados no cache local com `HF_HUB_OFFLINE=1`. As dependências do LuxTTS (`k2-fsa.github.io`) também estavam bloqueadas e foram puladas, sem efeito no Kokoro.
- **Peso**: o setup do Voicebox (torch e oito motores) é bem mais pesado que o do `kokoro-onnx`. Com a mesma voz `pf_dora`, o ganho real do Voicebox está nos outros motores, como clonar a voz do Eliel (Chatterbox Multilingual ou Qwen3-TTS, ambos com português), aplicar efeitos e usar o editor de stories. Esses motores não foram testados aqui porque os pesos deles só estão no Hugging Face.
