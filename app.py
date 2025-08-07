import streamlit as st
import pandas as pd
import requests

# スプレッドシートCSVを読み込む
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRrOkycGi4nVcR_f2HES6pkm4Yz8BiwFr2L9t3Zf0_j0c_eRy0g2pM9cxZj6fRfsUM20urikULvOqub/pub?output=csv"
books = pd.read_csv(csv_url)
books.columns = books.columns.str.strip() 

# 以下は今まで通りの処理
st.title("📘 今日のあなたに、そっとよりそう本をいっしょに探しましょう")


# 質問（順序・文言・選択肢を修正）
interest = st.selectbox(
    "まず、あなたが今 大切にしたいテーマを選んでください",
    (
        "自己理解・内省",
        "習慣・ライフスタイル",
        "仕事・キャリア",
        "人間関係・コミュニケーション",
        "恋愛・パートナーシップ",
        "子育て・教育",
        "死生観・人生の意味"
    )
)

feeling = st.radio(
    "そのテーマについて、今のあなたの心に近い気持ちを教えてください",
    (
        "前向きになりたい",
        "悩みを整理したい",
        "自分を深く知りたい",
        "人とよりよくつながりたい",
        "モヤモヤを晴らしたい"
    )
)

def get_book_thumbnail(title):
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:マツダミヒロ"
    try:
        response = requests.get(api_url)
        data = response.json()
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            image_links = volume_info.get("imageLinks", {})
            thumbnail = image_links.get("thumbnail")
            if thumbnail:
                return thumbnail
        return None
    except Exception:
        return None

import openai
from openai import OpenAI
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_reason(book, interest, feeling):
    prompt = f"""
あなたはマツダミヒロさん本人です。
読者に向けて、あなた自身の言葉として、以下の本をおすすめする文章（最大3文）を自然体で書いてください。

【条件】
- ユーザーの関心テーマ：{interest}
- ユーザーの今の気分：{feeling}
- 本のタイトル：{book['title']}
- 本の説明：{book['description']}
- 本のキーワード：{book['keywords']}

【お願い】
- 自分がその本をおすすめするような語り口にしてください（"私はこの本で〜と感じています" などは不要です）
- 詩的すぎず、やさしく寄り添う語り口で、読者に静かに届けるように語ってください。
- 「気づき」「問いかけ」「立ち止まる」などの自然な言葉を使っても構いません。
- 語尾は「〜かもしれませんね。」「〜してみるといいかもしれません。」など、押しつけのないやわらかい表現で。
- 「キミ」「あなた」などの直接的な呼びかけは使わずに、自然体な語りで締めくくってください。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはマツダミヒロの語り口で本をおすすめするアドバイザーです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=120
        )
        text = response.choices[0].message.content.strip()

        # 語尾ゆらぎ候補（自然な締めのバリエーションを追加）
        endings = [
            "かもしれません。",
            "かもしれませんね。",
            "のように感じます。",
            "のような気がします。",
            "があるような気がします。",
            "と感じることがあります。",
            "がふっと浮かんでくることもあります。",
            "がやさしく残るかもしれません。",
            "そっと心に留まるようです。",
            "ゆっくりと染み込んでくるような気がします。",
            "静かな余韻が広がるようです。",
            "そっと背中を押してくれる気がします。"
        ]

        # 文末が途中で切れていた場合や句読点がない場合の補完
        import random
        if not text.endswith(("。", "？", "！")) or text.endswith((
            "が", "の", "で", "と", "を", "に", "は", "も", "へ", "や", "から", "まで",
            "そして", "しかし", "けれど", "でも", "ながら"
        )):
            text += " " + random.choice(endings)

        # 語尾があまりに揃いすぎていたらゆらぎを追加（「かもしれ」判定を広げる）
        if text.count("かもしれ") >= 2:
            for target in ["かもしれません。", "かもしれませんね。"]:
                if target in text:
                    text = text.replace(target, random.choice(endings), 1)
                    break

        # 文末の重複語句を取り除く（例: "かもしれ かもしれませんね"）
        for phrase in ["かもしれ", "ですね", "ますね"]:
            if text.endswith(f"{phrase} {phrase}"):
                text = text.replace(f"{phrase} {phrase}", f"{phrase}", 1)

        # 不自然な語調微調整（例：末尾が "こと。" で切れている）
        if text.endswith("こと。こと。"):
            text = text[:-3] + "こと。"
        elif text.endswith(("ことが", "ことに", "ことで", "ことを", "ことの", "ことへ")):
            text += " なります。"

        # 教育用語をやわらかく抽象化
        replacements = {
            "思考力": "考えるきっかけ",
            "自主性": "自分で決める力",
            "論理的思考": "気づく力",
            "問題解決力": "自分で道を選ぶ感覚",
            "能力を伸ばす": "可能性に気づく",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

        # さらに語尾のゆらぎバリエーション
        soft_endings = [
            "のように感じます。",
            "のような気がします。",
            "があるような気がします。",
            "と感じることがあります。",
            "そっと心に留まるようです。",
            "ゆっくりと染み込んでくるような気がします。",
            "静かな余韻が広がるようです。",
            "そっと背中を押してくれる気がします。"
        ]

        # 柔らかい問いかけバリエーション（マツダミヒロさんの実際の問いかけスタイルに沿った新しい問い）
        gentle_questions = [
            "終わったあと、どんな気持ちでいたらうれしいですか？",
            "このページを閉じたとき、なにが残っていたら最高でしょう？",
            "今日という日、どんなふうに過ごしたいと思いますか？",
            "いま手放してもいいもの、なにかありますか？",
            "その問いが、どこへ導いてくれると感じますか？",
            "小さな余白、最近つくっていますか？",
            "最近、自分にどんな問いを投げかけましたか？",
            "“ちょっとだけうれしいこと”、浮かんできましたか？",
            "ほんの一歩だけでも、進んでみたいこと、ありますか？",
            "この問いを、自分に聞いてみたくなる瞬間って、ありますよね。"
        ]

        # 「かもしれませんね」で終わる場合のゆらぎ補正
        if text.endswith("かもしれませんね。"):
            if random.random() < 0.5:
                text = text.replace("かもしれませんね。", random.choice(soft_endings), 1)
            elif random.random() < 0.3:
                text = text.replace("かもしれませんね。", random.choice(gentle_questions), 1)

        # 文末が不自然な場合の補正（助詞＋語尾など）
        invalid_endings = ["があるような気がします", "のような気がします", "ことができるのような気がします"]
        preferred_endings = [
            "かもしれませんね。",
            "そっと差し出されているようです。",
            "静かに広がっていくかもしれません。",
            "やさしく寄り添ってくれるかもしれません。",
            "ふと心に残るかもしれませんね。"
        ]
        for invalid in invalid_endings:
            if text.endswith(invalid):
                text = text.replace(invalid, random.choice(preferred_endings))

        # 文末が助詞（「が」「の」など）で終わっていたら削除または補完
        if text.endswith((" が", " の", " を", " に", " は", " と")):
            text = text.rstrip(" がのをにはと") + "。"

        # 末尾の助詞＋動詞構文の崩れ対策（例："ことができるのような気がします"）
        text = text.replace("ことができるのような気がします", "ことができるかもしれませんね。")

        # 「〜気がします」系は避けて「かもしれませんね」系に変換
        soft_replacements = {
            "のような気がします。": "かもしれませんね。",
            "があるような気がします。": "かもしれませんね。",
            "と感じることがあります。": "かもしれませんね。",
            "のように感じます。": "かもしれませんね。"
        }
        for k, v in soft_replacements.items():
            if text.endswith(k):
                text = text[:-len(k)] + v

        # 「〜気がします。」という語尾を避ける（マツダミヒロさんの語り口に合わないため）
        # 明示的に末尾にあれば除去・置換
        if text.endswith("気がします。"):
            text = text[:-6] + "かもしれませんね。"
        elif text.endswith("気がします"):
            text = text[:-5] + "かもしれませんね。"

        # 文末の構文崩れ補正（例："がふっと浮かんでくることもあります" のように助詞と続く動詞が不自然な場合）
        # よくある不自然パターンを自然な表現に補う
        structure_fixes = {
            "がふっと浮かんでくることもあります": "が、ふっと浮かんでくることもあります。",
            "がそっと広がっていく": "が、そっと広がっていくかもしれませんね。",
            "へ": "へとつながっていくかもしれませんね。",
            "に": "に、やさしく導かれるかもしれませんね。",
            "と": "と、静かに問いかけてくるようです。",
            "を": "を、そっと差し出してくれているのかもしれません。",
            "が": "が、心に残るかもしれませんね。",
        }
        for broken, fixed in structure_fixes.items():
            if text.endswith(broken):
                text = text[:-len(broken)] + fixed

        # 文末が副詞で不自然に終わっている場合、自然な語尾で補完
        ending_adverbs = [
            "ゆっくりと", "静かに", "ふっと", "そっと", "じんわりと", "やさしく", "しずかに", "すっと"
        ]
        for adv in ending_adverbs:
            if text.endswith(adv):
                # ミヒロさんらしい語尾に限定
                adverb_completions = [
                    "そっと背中を押してくれるかもしれません。",
                    "静かな余韻が広がっていくかもしれませんね。",
                    "あたたかくよりそってくれるかもしれませんね。",
                    "その静けさが、そっと満ちていくかもしれませんね。"
                ]
                import random
                text = text + random.choice(adverb_completions)
                break

        # 禁止語「気がします」の完全排除
        for bad in ["気がします。", "気がします", "気がしてきますね。"]:
            if bad in text:
                text = text.replace(bad, "かもしれませんね。")

        # endings・soft_endings・adverb_completions からも除外
        endings = [e for e in endings if "気がします" not in e]
        soft_endings = [e for e in soft_endings if "気がします" not in e]
        adverb_completions = [
            "そっと背中を押してくれるかもしれません。",
            "静かな余韻が広がっていくかもしれませんね。",
            "あたたかくよりそってくれるかもしれませんね。",
            "その静けさが、そっと満ちていくかもしれませんね。"
        ]
        adverb_completions = [e for e in adverb_completions if "気がします" not in e]

        # --- 不自然な語尾（助詞＋かもしれませんね）補正 ---
        awkward_phrases = [
            "のようなかもしれませんね。",
            "があるようなかもしれませんね。",
            "に想 かもしれませんね。",
            "というかもしれませんね。",
            "ようなようなかもしれませんね。"
        ]
        for phrase in awkward_phrases:
            if phrase in text:
                text = text.replace(phrase, "かもしれませんね。")

        # 「かもしれませんね。」の出現数が2回以上なら、2回目以降を別語尾に置き換える
        cm_count = text.count("かもしれませんね。")
        if cm_count >= 2:
            alt_endings = [
                "だったらうれしいですね。",
                "そっと問いかけてくれているようです。",
                "ふと心に響くようです。",
                "そんな余白があってもいいですね。",
            ]
            parts = text.split("かもしれませんね。")
            for i in range(1, len(parts)):
                if i < len(alt_endings):
                    parts[i] = alt_endings[i - 1] + parts[i]
            text = "".join(parts)

        # --- 構文崩れ補正①：「〜なるだったらうれしい」など助動詞の破綻 ---
        text = text.replace("なるだったらうれしいですね。", "なれたらうれしいですね。")
        text = text.replace("なるだったらうれしいですね", "なれたらうれしいですね")
        text = text.replace("なるだったらうれしい", "なれたらうれしい")

        # --- 構文崩れ補正②：接続詞がなく2文が合体している不自然な箇所を分割 ---
        text = text.replace("するそっと", "する。そっと")
        text = text.replace("なるそっと", "なる。そっと")
        text = text.replace("導くそっと", "導く。そっと")
        text = text.replace("広がるそっと", "広がる。そっと")
        text = text.replace("浮かぶそっと", "浮かぶ。そっと")

        # 「そっと」が2回以上使われていたら、最初の1つを自然な言い換えに置き換える
        if text.count("そっと") >= 2:
            alternative_soft = ["静かに", "ふと", "やわらかく", "ゆるやかに", "そよぐように"]
            text = text.replace("そっと", random.choice(alternative_soft), 1)

        # --- ① カジュアルすぎる語尾の検出と置換 ---
        casual_endings = {
            "かもです。": "かもしれませんね。",
            "かもです": "かもしれませんね。",
            "だよ。": "。",
            "だよ": "",
            "んだ。": "。",
            "んだ": "",
        }
        for bad, replacement in casual_endings.items():
            if text.endswith(bad):
                text = text[:-len(bad)] + replacement

        # --- ② 副詞が2語以上連続した場合、最初の1つを削除 ---
        soft_adverbs = ["そっと", "ふと", "一度", "やさしく"]
        for adv in soft_adverbs:
            if text.count(adv) >= 2:
                text = text.replace(adv, "", 1)

        # --- ③ 助動詞・助詞の組み合わせ崩れを補正 ---
        text = text.replace("くれるだったらうれしい", "くれたらうれしい")
        text = text.replace("してくれるだったらうれしい", "してくれたらうれしい")
        text = text.replace("与えてくれるだったらうれしい", "与えてくれたらうれしい")

        # --- 文末が動詞で不自然に切れているとき、自動で補完 ---
        if text.endswith("生"):
            text = text[:-1] + "まれるかもしれませんね。"
        elif text.endswith("踏み"):
            text = text + "出してみるのもいいかもしれませんね。"

        # --- 文末が助詞や動詞で終わっていても自然な文に補完 ---
        broken_endings = {
            "が生": "が生まれてくるかもしれませんね。",
            "を踏み": "を踏み出してみたくなるかもしれませんね。",
            "を開き": "を開いてみたくなるかもしれませんね。",
        }
        for k, v in broken_endings.items():
            if text.endswith(k):
                text = text[:-len(k)] + v

        # --- ① 「そっと心に留まるようです」の語尾が多すぎる場合に他の語尾へ差し替え ---
        if text.count("そっと心に留まるようです") >= 2:
            alt_phrases = [
                "静かに響いてくるかもしれませんね。",
                "ふと立ち止まりたくなる一冊かもしれません。",
                "やさしく寄り添ってくれるかもしれませんね。",
                "少しずつ心に残る本かもしれません。"
            ]
            import random
            text = text.replace("そっと心に留まるようです", random.choice(alt_phrases), 1)

        # --- ② カジュアル語（「キミ」「〜だよ」「〜んだ」など）の完全排除 ---
        casual_words = {
            "キミ": "",
            "だよ。": "。",
            "だよ": "",
            "んだ。": "。",
            "んだ": "",
        }
        for bad, replacement in casual_words.items():
            text = text.replace(bad, replacement)

        return text
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        print(f"OpenAI API error: {e}")
        return "（おすすめ理由の生成中にエラーが発生しました）"

import urllib.parse

if st.button("📖 今のあなたに合う本をえらんでみる"):
    # ユーザーの選択に合う本をフィルタリング
    filtered_books = books[
        books["keywords"].str.contains(interest, na=False) &
        books["keywords"].str.contains(feeling, na=False)
    ]

    # フィルタ後に本を選ぶ（足りない場合は全体から）
    if len(filtered_books) >= 3:
        top_pick = filtered_books.sample(1).iloc[0]
        other_picks = filtered_books.drop(top_pick.name).sample(2)
    elif len(filtered_books) >= 1:
        top_pick = filtered_books.sample(1).iloc[0]
        other_picks = books.drop(top_pick.name).sample(2)
    else:
        top_pick = books.sample(1).iloc[0]
        other_picks = books.drop(top_pick.name).sample(2)

    st.success("この3冊のなかに、いまのあなたにやさしく語りかけてくれる本があるかもしれません。")
    st.markdown(f"📝 **あなたが選んだテーマと気持ちから、こんな本たちが浮かびました。**\n\nテーマ：『{interest}』\n気持ち：『{feeling}』")

    st.markdown("## 🌟 今のあなたに、いちばん届けたい1冊")
    thumbnail_url = get_book_thumbnail(top_pick.title)
    if thumbnail_url:
        st.image(thumbnail_url, width=150)
    else:
        st.markdown("📘 ※ 表紙画像が見つかりませんでした。")
    st.markdown(f"### 『{top_pick.title}』")
    query_top = urllib.parse.quote_plus(f"{top_pick['title']} マツダミヒロ")
    amazon_search_url_top = f"https://www.amazon.co.jp/s?k={query_top}"
    st.markdown(f"[📦 Amazonで検索する]({amazon_search_url_top})")
    st.markdown(f"💬 **本の概要：** {top_pick['description']}")

    st.markdown("## 📚 よかったら、こんな本も見てみませんか？")
    for index, book in other_picks.iterrows():
        st.markdown("---")
        thumbnail_url = get_book_thumbnail(str(book["title"]))
        if thumbnail_url:
            st.image(thumbnail_url, width=150)
        else:
            st.markdown("📘 ※ 表紙画像が見つかりませんでした。")
        st.markdown(f"### 『{book['title']}』")
        query = urllib.parse.quote_plus(f"{book['title']} マツダミヒロ")
        amazon_search_url = f"https://www.amazon.co.jp/s?k={query}"
        st.markdown(f"[📦 Amazonで検索する]({amazon_search_url})")
        st.markdown(f"💬 **本の概要：** {book['description']}")