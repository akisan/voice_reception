# voice_reception

## 処理の流れ

1. SpeechRecognition で音声をテキスト化します。
1. MeCab を使って形態素解析を行い、テキストから人名を抽出します。
1. 抽出した人名に一致するユーザーを検索します。
1. 検索結果を表示します。

## 使い方

仮想環境を作成＆有効化し、パッケージをインストールします。

```bash
$ cd voice_reception
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) >python -m pip install -r requirements.txt
```

Mac の場合は、次をインストールします。

ERROR: Could not build wheels for pyaudio, which is required to install pyproject.toml-based projects

OSError: FLAC conversion utility not available - considmermaier installing the FLAC command line application by running `apt-get install flac` or your operating system's equivalent

```bash
brew install portaudio flac
```

Linux 　の場合は、次をインストールします。

```bash
apt install python-pyaudio python3-pyaudio
```

main.py を実行します。

```bash
(.venv) >python main.py
```
