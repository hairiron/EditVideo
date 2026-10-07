import os
import subprocess
from pathlib import Path


def extract_all_text_with_coordinates(keynote_path, output_txt_path):
    abs_keynote_path = os.path.abspath(keynote_path)
    abs_output_path = os.path.abspath(output_txt_path)

    # 構文エラーを回避するため、「every iWork item」に変更し、
    # ループ変数（aShape）が正しく要素を指すように修正
    applescript = f"""
    tell application "Keynote"
        set openDoc to open POSIX file "{abs_keynote_path}"
        set extractedText to ""
        
        tell openDoc
            set slideIndex to 1
            repeat with aSlide in slides
                -- 「every iWork item」と明示して構文エラーを回避
                set allItems to every iWork item of aSlide
                set isOutputPage to "no"
                
                repeat with aShape in allItems
                    set shapeText to ""
                    set posX to "不明"
                    set posY to "不明"
                    
                    -- 1. テキストの取得を試みる
                    try
                        set shapeText to object text of aShape
                    end try
                    
                    -- テキストが存在する場合のみ進む
                    if shapeText is not "" and shapeText is not missing value then
                        -- 2. 座標の取得を試みる
                        try
                            set pos to position of aShape
                            set posX to item 1 of pos
                            set posY to item 2 of pos
                        end try

                        if posX is 93 and posY is 840 then
                            set infoLine to "あんこもん（ノーマル）," & shapeText
                            set extractedText to extractedText & infoLine & linefeed
                            set isOutputPage to "yes"
                        else if posX is 505 and posY is 853 then
                            set infoLine to "ずんだもん（ノーマル）," & shapeText
                            set extractedText to extractedText & infoLine & linefeed
                            set isOutputPage to "yes"
                        else
                            set infoLine to "[" & slideIndex & "枚目] (X:" & posX & ", Y:" & posY & "): " & shapeText
                        end if

                    end if
                end repeat
                if isOutputPage is "no" then
                    set infoLine to "[" & slideIndex & "枚目]"
                    set extractedText to extractedText & infoLine & linefeed
                end if
                set slideIndex to slideIndex + 1
            end repeat
        end tell
        
        close openDoc saving no
    end tell
    
    return extractedText
    """

    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            check=True,
        )

        if not result.stdout.strip():
            print(
                "⚠️ スクリプトは完了しましたが、テキストが1件も取得できませんでした。"
            )
            print(
                "Keynote内の文字が「グループ化」や「表（テーブル）」の中にある可能性があります。"
            )
        else:
            with open(abs_output_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print(f"🎉 成功しました！ファイルを出力しました: {abs_output_path}")

    except subprocess.CalledProcessError as e:
        print("❌ AppleScriptの実行中にエラーが発生しました。")
        print("【エラー内容 (stderr)】")
        print(e.stderr)


# パスの指定
documents_path = Path.home() / "Documents"
file_path = documents_path / "マスタ.key"
output_file_path = documents_path / "target_output.txt"

extract_all_text_with_coordinates(file_path, output_file_path)
