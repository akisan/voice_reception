import MeCab
import csv
import speech_recognition as sr


def read_csv_file(file_name: str) -> list[list[str]]:
    """CSVデータをファイルから読み込む

    Args:
        file_name (str): ファイルパス

    Returns:
        list[list[str]]: CSVレコードのリスト
    """
    data = []
    with open(file_name, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data


tagger = MeCab.Tagger("-Owakati")


def extract_nouns(text: str) -> list[str]:
    """人名を抽出します。

    Args:
        text (str): テキスト

    Returns:
        list[str]: 人名のリスト
    """
    nouns = []
    node = tagger.parseToNode(text)
    while node:
        if node.feature.startswith("名詞") and "人名" in node.feature:
            if node.surface not in nouns:
                nouns.append(node.surface)
        node = node.next
    return nouns


if __name__ == "__main__":
    file_name = "users.csv"
    data = read_csv_file(file_name)
    print("読み込んだデータ: ", data)

    names = []
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("話してください:")
        while True:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            print("音声認識中...")
            try:
                text = r.recognize_google(audio, language="ja-JP")
                print("あなたが言ったこと: " + text)
                names = list(set(names + extract_nouns(text)))
                print("人名: " + names)
                filtered_data = [
                    record for record in data if any(name in record for name in names)
                ]
                print("検索結果: " + filtered_data)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(
                        e
                    )
                )
