import cv2
import numpy as np
from src import ImageProcessor

def main():
    INPUT_PATH = "assets/sample.jpg" 
    OUTPUT_SWAPPED_PATH = "assets/output_swapped.jpg"

    print("--- BẮT ĐẦU QUY TRÌNH XỬ LÝ ẢNH ---")

    def wait_step():
        print(">> [Tạm dừng] Nhấn phím bất kì trên cửa sổ ảnh để sang bước tiếp theo...\n")
        cv2.waitKey(0)

    def print_img_info(name, img_matrix):
        """In thông tin kích thước và kênh màu của một ma trận ảnh"""
        h, w = img_matrix.shape[:2]
        
        if len(img_matrix.shape) == 2:
            c = 1
        else:
            c = img_matrix.shape[2] 
            
        print(f"   -> [Kết quả] Ảnh {name}: Rộng {w}px, Cao {h}px, Số kênh: {c}")

    try:
        processor = ImageProcessor(INPUT_PATH)

        print("[1] Đang hiển thị ảnh gốc...")
        print_img_info("Gốc", processor.image) 
        processor.show_image("1. Anh goc")
        wait_step()

        print("[2] Đang tách các kênh màu (R-G-B)...")
        print("   -> [Kết quả] Đã tách thành 3 cửa sổ riêng biệt (Mỗi ảnh 3 kênh, nhưng chỉ giữ 1 màu)")
        processor.show_separate_channels()
        wait_step()

        print("[3] Đang chuyển đổi hệ màu BGR -> RGB...")
        swapped_img = processor.swap_channels(order="RGB")
        
        print_img_info("Đảo kênh (RGB)", swapped_img)
        
        processor.show_image("2. Anh RGB", swapped_img)
        processor.save_image(swapped_img, OUTPUT_SWAPPED_PATH)
        wait_step()

        print("[4] Đang chuyển sang ảnh xám...")
        gray_img = processor.to_grayscale()
        
        print_img_info("Xám ", gray_img)
        
        processor.show_image("3. Anh xam ", gray_img)
        wait_step()

        print("[5] Đang chuyển sang ảnh nhị phân (Đen/Trắng)...")
        binary_img = processor.to_binary(threshold_val=127)
        
        print_img_info("Nhị phân (Binary)", binary_img)
        
        processor.show_image("4. Anh nhi phan ", binary_img)
        
        print("--- HOÀN TẤT QUY TRÌNH. NHẤN PHÍM BẤT KỲ ĐỂ THOÁT ---")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"[Lỗi] Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    main()