from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import sounddevice as sd
import paho.mqtt.client as mqtt

# MQTT設定
host = "mqtt.isc.ac.jp"
port = 1883
MQTT_USER = "isc"
MQTT_PASS = "iwasaki3_"

# MQTTクライアント準備
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(host, port, keepalive=60)

encoder = VoiceEncoder()

# 事前に本人の声を録音して保存しておく
ref_wav = preprocess_wav("rec.wav")
ref_emb = encoder.embed_utterance(ref_wav)


def trim_silence(
    wav,
    threshold=0.02,
    chunk_size=160,
    buffer_chunks=2
):
    # ステレオの場合は mono 化
    if wav.ndim == 2:
        wav = wav.mean(axis=1)

    abs_wav = np.abs(wav)

    energies = np.array([
        abs_wav[i:i+chunk_size].mean()
        for i in range(0, len(abs_wav), chunk_size)
    ])

    # 閾値を超えるチャンク
    idx = np.where(energies > threshold)[0]

    if len(idx) == 0:
        return wav  # 無音だけならそのまま

    # バッファを追加
    start = max((idx[0] - buffer_chunks) * chunk_size, 0)
    end = min((idx[-1] + 1 + buffer_chunks) * chunk_size, len(wav))

    return wav[start:end]


def record(seconds=3):
    print("録音開始…事前に録音したときと同じように喋ってね")
    audio = sd.rec(int(seconds * 16000), samplerate=16000, channels=1)
    sd.wait()
    print("録音終了")
    audio = np.squeeze(audio)

    # 無音カット
    audio = trim_silence(audio)
    return audio

ref_wav = trim_silence(ref_wav)
while True:
    wav = record(6)

    if len(wav) < 3000:
        print("音声が短すぎる…もう一度録音してね")
        continue

    emb = encoder.embed_utterance(wav)
    dist = np.linalg.norm(ref_emb - emb)

    print("距離:", dist)
    #本人確認出来たら
    if dist < 0.6:
        print("→ 本人の可能性が高いよ！ ペットへコマンドを送信するよ！")
        client.publish("iottaiken/mabee", "1,on")
    else:
        print("→ 本人ではない可能性が高いよ")
        client.publish("iottaiken/mabee", "1,off")
