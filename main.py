import os
import sys
import chardet
import argparse
import tkinter as tk
from tkinter import filedialog
import logging
from datetime import datetime

# 獲取專案目錄
# PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# 確定專案目錄
if getattr(sys, 'frozen', False):
    # 如果程式被打包
    PROJECT_DIR = os.path.dirname(sys.executable)
else:
    # 如果程式作為腳本運行
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# 創建日誌目錄
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 設置日誌
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(LOG_DIR, f'app_log_{current_time}.txt')
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    logging.debug(f"檔案 {file_path} 的編碼偵測結果：{result['encoding']} (信心度：{result['confidence']})")
    return result['encoding']

def read_file(file_path):
    detected_encoding = detect_encoding(file_path)
    try:
        with open(file_path, 'r', encoding=detected_encoding) as file:
            content = file.read()
        logging.debug(f'成功讀取 {len(content)} 個字符，使用 {detected_encoding} 編碼')
        return content
    except Exception as e:
        logging.error(f'讀取檔案 {file_path} 時發生錯誤：{e}')
        return None

def convert_to_big5(content):
    try:
        big5_content = content.encode('big5', errors='replace')
        logging.debug(f'轉換為 Big5 編碼，長度：{len(big5_content)} 位元組')
        return big5_content
    except Exception as e:
        logging.error(f'轉換為 Big5 編碼時發生錯誤：{e}')
        return None

def write_big5_file(file_path, content):
    try:
        with open(file_path, 'wb') as file:
            file.write(content)
        logging.debug(f'寫入 {len(content)} 位元組到 {file_path}')
    except Exception as e:
        logging.error(f'寫入檔案 {file_path} 時發生錯誤：{e}')

def verify_big5_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read().decode('big5')
        logging.debug(f"成功以 Big5 編碼讀取檔案 {file_path}")
        logging.debug(f"檔案內容預覽：\n{content[:100]}...")  # 只顯示前100個字符
    except UnicodeDecodeError:
        logging.error(f"無法以 Big5 編碼讀取檔案 {file_path}")
    except Exception as e:
        logging.error(f"讀取檔案 {file_path} 時發生錯誤：{e}")

def process_punish_file(content):
    lines = content.split('\n')
    # 移除第一行
    if lines:
        lines = lines[1:]
    
    # 從末尾開始移除空行和 '@@'行
    while lines and (not lines[-1].strip() or lines[-1].strip() == '@@'):
        lines.pop()

    # 移除中間的空行
    lines = [line for line in lines if line.strip()]

    return '\n'.join(lines)

def process_file(file_path, output_dir=None):
    content = read_file(file_path)
    if content is None:
        return None

    logging.debug(f'原始內容預覽：\n{content[:100]}...')

    if'Punish-' in os.path.basename(file_path):
        content = process_punish_file(content)
        logging.debug(f'處理後的 Punish 文件內容預覽：\n{content[:100]}...')

    big5_content = convert_to_big5(content)
    if big5_content is None:
        return None
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, os.path.basename(file_path))
    else:
        output_path = os.path.splitext(file_path)[0] + '_BIG5.txt'

    write_big5_file(output_path, big5_content)

    logging.debug("驗證輸出檔案：")
    verify_big5_file(output_path)

    return output_path

def select_files():
    logging.debug("進入 select_files 函數")
    root = tk.Tk()
    root.withdraw()  # 隱藏主窗口
    files = filedialog.askopenfilenames(title="選擇文件", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    logging.debug(f"選擇的文件: {files}")
    return files

def main():
    logging.debug("進入 main 函數")
    parser = argparse.ArgumentParser(description='將檔案轉換為 Big5 編碼。')
    parser.add_argument('files', nargs='*', help='要轉換的輸入檔案')
    parser.add_argument('-o', '--output', help='輸出目錄（可選）')
    args = parser.parse_args()

    logging.debug(f"命令行參數: {args}")

    if not args.files:
        logging.debug("沒有提供文件，調用 select_files")
        args.files = select_files()

    if not args.files:
        logging.debug("沒有選擇任何文件，程式結束")
        print("沒有選擇任何文件，程式結束。")
        return

    for file in args.files:
        if not os.path.exists(file):
            logging.error(f'錯誤：檔案 {file} 不存在')
            print(f'錯誤：檔案 {file} 不存在')
            continue
        
        output_file = process_file(file, args.output)
        if output_file:
            logging.info(f'成功將 {file} 轉換為 {output_file}')
            print(f'成功將 {file} 轉換為 {output_file}')
        else:
            logging.error(f'轉換 {file} 失敗')
            print(f'轉換 {file} 失敗')
        logging.debug('-' * 50)
        print('-' * 50)

if __name__ == "__main__":
    logging.debug("程序開始執行")
    main()
    logging.debug("程序結束執行")