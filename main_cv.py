from typing import Optional

import cv2
import concurrent.futures
import imutils
import numpy as np
import progressbar
import os
import queue
import subprocess
import sys
import tesserocr
import textract
import time
from io import BytesIO
from pdf2image import convert_from_path
from resources.pledgeclass import Pledge
from resources.pledgemethods import clear_cache, find_last

tesserocr_queue = queue.Queue()
THREAD_COUNT = 3


def process_ocr(img) -> Optional[list]:
    api = None
    try:
        api = tesserocr_queue.get(block=True, timeout=300)
        api.SetImage(img)
        return [x.strip() for x in api.GetUTF8Text().split('\n') if len(x)]
    except queue.Empty:
        return None
    finally:
        if api is not None:
            tesserocr_queue.put(api)


def main():
    # 0:43-0:46 benchmark with tesserocr and multithreading (3 threads)

    PDF_PATH = 'resources/temp.pdf'

    print("Converting from pdf to images...")
    pages = convert_from_path(PDF_PATH, 100)

    print("Starting multithreaded OCR...")
    for _ in range(THREAD_COUNT):
        tesserocr_queue.put(tesserocr.PyTessBaseAPI())
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        results = executor.map(process_ocr, pages)
    for _ in range(THREAD_COUNT):
        api = tesserocr_queue.get(block=True)
        api.End()
    tesserocr_queue.queue.clear()

    text = [x for p in results for x in p]
    print(text)
    quit()
    PLEDGE_COUNT = int(text[text.index('TOTAL PLEDGES:') + 8])
    print(PLEDGE_COUNT)

    quit()
    TOTAL_AMT = float(''.join([i for i in text[find_last(text, "Total Amount:") + 1] if i not in ['$', ',']]))



    # print_progress_bar(0, len(text_pages), "Parsing text for pledges...")
    # for i, page in enumerate(text_pages):
    #     if i==len(text_pages)-1:
    #         break

    ###################################
    # pledge_sum = sum([p.amount for p in pledges])
    # out_str = '\n'.join([str(p) for p in pledges])
    # print(out_str)
    #
    # # Printing some diagnostic information to ensure data is correct
    # if pledge_sum != total_amt:
    #     print(f"\nIncorrect total amount; Expected {'${:,.2f}'.format(total_amt)}, got {'${:,.2f}'.format(pledge_sum)}")
    # else:
    #     print(f"\nTotal amount: {'${:,.2f}'.format(total_amt)}")
    #
    # pledge_list_count = len(pledges)
    # if pledge_list_count != pledge_count:
    #     print(f"Incorrect pledge count; Expected {pledge_count}, got {pledge_list_count}\n")
    # else:
    #     print(f"Pledge count: {pledge_count}\n")
    #
    # subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    # print('Lines copied to keyboard!')
    ###################################

if __name__ == '__main__':
    clear_cache()
    main()
    clear_cache()
