import math
from pypdf import PageObject, PdfReader, PdfWriter


def make_booklet_a3(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # 元のページのサイズ（A5）を取得
    first_page = reader.pages[0]
    a5_width = float(first_page.mediabox.width)
    a5_height = float(first_page.mediabox.height)

    # 出力するA3（2×2配置）のサイズ設定
    a3_width = a5_width * 2
    a3_height = a5_height * 2

    num_original_pages = len(reader.pages)
    # 8の倍数に切り上げ（不足分は空白ページ）
    num_sheets = math.ceil(num_original_pages / 8)
    total_pages = num_sheets * 8

    # ページ取得用のヘルパー関数（1ベースのページ番号から0ベースのPageObjectを取得）
    def get_page_obj(p_num):
        if p_num <= num_original_pages:
            return reader.pages[p_num - 1]
        else:
            # 元のページ範囲を超える場合は空白ページを作成
            return PageObject.create_blank_page(
                width=a5_width, height=a5_height
            )

    # A3ページ上の 2x2 位置にページを配置する関数
    # pos: "top_left", "top_right", "bottom_left", "bottom_right"
    def place_page(target_a3_page, source_page, pos):
        x_offset = 0 if "left" in pos else a5_width
        y_offset = a5_height if "top" in pos else 0
        target_a3_page.merge_translated_page(source_page, x_offset, y_offset)

    # 用紙（Sheet）ごとに表裏を生成
    for i in range(1, num_sheets + 1):
        N = num_sheets

        # --- 各位置のページ番号を計算（1ベース） ---
        # 表面
        front_tl = 8 * N - 2 * (i - 1)
        front_tr = 2 * i - 1
        front_bl = 4 * N - 2 * (i - 1) - 1
        front_br = 4 * N + 2 * i

        # 裏面
        back_tl = 2 * i
        back_tr = 8 * N - 2 * (i - 1) - 1
        back_bl = 4 * N + 2 * i - 1
        back_br = 4 * N - 2 * (i - 1)

        # --- 表面（Front）の作成 ---
        sheet_front = PageObject.create_blank_page(
            width=a3_width, height=a3_height
        )
        place_page(sheet_front, get_page_obj(front_tl), "top_left")
        place_page(sheet_front, get_page_obj(front_tr), "top_right")
        place_page(sheet_front, get_page_obj(front_bl), "bottom_left")
        place_page(sheet_front, get_page_obj(front_br), "bottom_right")
        writer.add_page(sheet_front)

        # --- 裏面（Back）の作成 ---
        sheet_back = PageObject.create_blank_page(
            width=a3_width, height=a3_height
        )
        place_page(sheet_back, get_page_obj(back_tl), "top_left")
        place_page(sheet_back, get_page_obj(back_tr), "top_right")
        place_page(sheet_back, get_page_obj(back_bl), "bottom_left")
        place_page(sheet_back, get_page_obj(back_br), "bottom_right")
        writer.add_page(sheet_back)

    # ファイルへ書き出し
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"変換が完了しました: {output_pdf_path}")
    print(
        f"総ページ数: {num_original_pages} -> A3用紙 {num_sheets} 枚（両面刷り）"
    )


# --- 実行 ---
if __name__ == "__main__":
    make_booklet_a3("input.pdf", "output_a3_booklet.pdf")
