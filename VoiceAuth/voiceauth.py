from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import sounddevice as sd

encoder = VoiceEncoder()

# 事前に本人の声を録音して保存しておく
ref_wav = preprocess_wav("../rec.wav")
ref_emb = encoder.embed_utterance(ref_wav)

def trim_silence(wav, threshold=0.02, chunk_size=160):
    """
    wav: numpy array (float)
    threshold: 無音判定の振幅
    chunk_size: 一度に見るサンプル数（10ms程度）
    """
    # 絶対値を取る
    abs_wav = np.abs(wav)

    # チャンク単位のエネルギーで判定
    energies = np.array([
        abs_wav[i:i+chunk_size].mean()
        for i in range(0, len(abs_wav), chunk_size)
    ])

    # 音があるチャンクを抽出
    idx = np.where(energies > threshold)[0]

    if len(idx) == 0:
        # 全部無音だった場合そのまま返す
        return wav

    start = idx[0] * chunk_size
    end = min((idx[-1] + 1) * chunk_size, len(wav))

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

while True:
    wav = record(4)

    # 無音が極端に短い場合の対策
    if len(wav) < 5000:
        print("音声が短すぎるにゃ…もう一度録音するにゃ")
        continue

    emb = encoder.embed_utterance(wav)
    dist = np.linalg.norm(ref_emb - emb)

    print("距離:", dist)

    if dist < 0.6:
        print("→ 本人の可能性が高いにゃ！")
    else:
        print("→ 本人ではない可能性が高いにゃ")
