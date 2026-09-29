from pypdf import PdfReader, PdfWriter, PageObject
import math

def generate_imposition_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    # 8の倍数になるよう総ページ数を切り上げ
    padded_total = math.ceil(total_pages / 8) * 8
    
    writer = PdfWriter()
    
    # 1枚のA3（8ページ分）を繰り返し作成
    # sheet_idx: 0, 1, 2... (シート単位)
    num_sheets = padded_total // 8
    
    for s in range(num_sheets):
        # 該当シートの8つのページ番号を計算 (1-indexed)
        # 上段：外側と内側を巻き込む中綴じ折り
        # 下段：もう1セットの中綴じ折り
        p1 = 8 * s + 8
        p2 = 8 * s + 1
        p3 = 8 * s + 3
        p4 = 8 * s + 6
        
        p5 = 8 * s + 2
        p6 = 8 * s + 7
        p7 = 8 * s + 4
        p8 = 8 * s + 5
        
        page_map_front = [p1, p2, p3, p4] # [左上, 右上, 左下, 右下]
        page_map_back  = [p5, p6, p7, p8] # [左上, 右上, 左下, 右下]

        # 表面と裏面を作成
        for page_map in [page_map_front, page_map_back]:
            # A5サイズ基準 (Pt単位: 420 x 595 pt 前後)
            # 最初の有効ページからサイズを取得、無ければデフォルト(A5)
            sample_page = reader.pages[0]
            a5_w = float(sample_page.mediabox.width)
            a5_h = float(sample_page.mediabox.height)
            
            # A3キャンバス（横長：A5幅×2、A5高さ×2）を作成
            a3_w = a5_w * 2
            a3_h = a5_h * 2
            a3_page = PageObject.create_blank_page(width=a3_w, height=a3_h)
            
            # 4領域の配置座標 (x, y) - 左下が原点
            # 左上: (0, a5_h),  右上: (a5_w, a5_h)
            # 左下: (0, 0),     右下: (a5_w, 0)
            positions = [
                (0, a5_h),       # 左上
                (a5_w, a5_h),    # 右上
                (0, 0),          # 左下
                (a5_w, 0)        # 右下
            ]
            
            for p_num, (x, y) in zip(page_map, positions):
                if p_num <= total_pages:
                    # 元のページをコピーして配置
                    src_page = reader.pages[p_num - 1]
                    a3_page.merge_translated_page(src_page, tx=x, ty=y)
                # p_num > total_pages の場合は白紙（何もしない）
            
            writer.add_page(a3_page)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    print(f"完了: '{output_path}' に保存されました。（総A3面数: {num_sheets * 2}面）")

# 実行例
if __name__ == "__main__":
    # 入力ファイル名と出力ファイル名を指定
    generate_imposition_pdf("input_a5.pdf", "output_a3_imposed.pdf")
