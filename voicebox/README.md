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

## Teste de clonagem de voz (13/10/2026, só CPU)

Referência: 13,6 s de uma locução (locutor com autorização), com a transcrição exata. Os arquivos de referência e os áudios clonados **não** ficam no repositório.

| Motor | Radar de exemplo | Tempo de geração | Velocidade |
|---|---|---|---|
| Kokoro `pf_dora` (voz pronta) | 40 s | ~19 s | ~2x mais rápido que o tempo real |
| Chatterbox Multilingual (clone) | 40 s | ~3 min 52 s | ~6x mais lento que o tempo real |
| Qwen3-TTS 0.6B (clone) | 45 s | ~4 min 8 s | ~5,5x mais lento que o tempo real |

Os dois clones ficaram inteligíveis (conferido com Whisper). **Na avaliação do Eliel, o clone do Qwen3-TTS ficou bem melhor** e é o motor escolhido para os próximos passos. Na CPU, um podcast de 3 minutos levaria cerca de 17 a 18 minutos, acima do limite de 15 minutos da seção 7D. Para usar clone no Radar, aumente esse limite ou rode o Voicebox numa máquina com GPU.

Como criar o perfil clonado:

```
curl -X POST localhost:17493/profiles -H 'Content-Type: application/json' -d '{"name":"Locutor Clone","language":"pt","voice_type":"cloned","default_engine":"chatterbox"}'
curl -X POST localhost:17493/profiles/<id>/samples -F file=@referencia.wav -F "reference_text=<transcrição exata>"
VOICEBOX_PROFILE="Locutor Clone" VOICEBOX_ENGINE=chatterbox python radar_audio_voicebox.py saida.mp3 /tmp/radar.json
# ou: VOICEBOX_ENGINE=qwen VOICEBOX_MODEL_SIZE=0.6B
```

Correções necessárias neste ambiente:
- `uv pip install --no-deps chatterbox-tts` e `uv pip install "setuptools<81"`. Sem o `pkg_resources`, o watermarker do Chatterbox não carrega (`'NoneType' object is not callable`).
- Qwen3-TTS: o download pelo Voicebox falhou em modo offline. Baixar antes com `huggingface_hub.snapshot_download` de `Qwen/Qwen3-TTS-12Hz-0.6B-Base` e `Qwen/Qwen3-TTS-Tokenizer-12Hz` resolve.
- O `/transcribe` do Voicebox falha na CPU com esta versão do torch (erro de "meta tensor"). A transcrição da referência foi feita direto com o `transformers` (`openai/whisper-small`).

## Observações

- **Python 3.12**: o pacote `kokoro` exigido pelo Voicebox não instala no Python 3.13.
- **Rede**: o Voicebox baixa os modelos do Hugging Face. No ambiente deste teste o `huggingface.co` estava bloqueado; os pesos do Kokoro (`kokoro-v1_0.pth`, `config.json`) e a voz `pf_dora.pt` vieram de espelhos no GitHub (releases do `remsky/Kokoro-FastAPI`) e foram colocados no cache local com `HF_HUB_OFFLINE=1`. As dependências do LuxTTS (`k2-fsa.github.io`) também estavam bloqueadas e foram puladas, sem efeito no Kokoro.
- **Peso**: o setup do Voicebox (torch e oito motores) é bem mais pesado que o do `kokoro-onnx`. Com a mesma voz `pf_dora`, o ganho real do Voicebox está nos outros motores, como clonar a voz do Eliel (Chatterbox Multilingual ou Qwen3-TTS, ambos com português), aplicar efeitos e usar o editor de stories. Esses motores não foram testados aqui porque os pesos deles só estão no Hugging Face.

## Integração na seção 7D (pendente: download da amostra)

A seção 7D do README principal já usa o Qwen3-TTS 0.6B com a voz clonada, um limite de 22 minutos e a pf_dora de reserva. As regras de pronúncia estão na seção 7A (EDZ vira "é dê zê" e as outras siglas também são escritas como se falam). Falta definir como cada execução copia a amostra `voz_ref.ogg` do Google Drive para `/tmp/voz_ref.ogg`. Opções:

1. Gerar um novo refresh token OAuth com os escopos `gmail.send` e `drive.readonly` e baixar pela API do Drive (`files/<id>?alt=media`), com o ID do arquivo numa variável de ambiente (`VOZ_DRIVE_ID`).
2. Compartilhar o arquivo por link e baixá-lo com o ID numa variável de ambiente. É mais simples, mas qualquer pessoa com o link consegue baixar a voz.

Enquanto isso não for definido, `/tmp/voz_ref.ogg` não existe e o Radar sai com a pf_dora.
