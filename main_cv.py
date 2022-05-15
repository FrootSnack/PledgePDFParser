import concurrent.futures
import queue
import subprocess
import tesserocr
from pdf2image import convert_from_path
from resources.pledgeclass import Pledge
from resources.pledgemethods import clear_cache, find_nth_containing
from typing import Optional

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


def main(pdf_path='resources/temp.pdf'):
    # 0:43-0:46 benchmark with tesserocr and multithreading (3 threads)

    # TODO: Add back command line arguments and checks to make sure provided file is a pdf
    # TODO: Rewrite this whole thing. Use this stackoverflow answer.
    #  https://stackoverflow.com/questions/50579050/template-matching-with-multiple-objects-in-opencv-python/58514954#58514954
    #  Use OpenCV and pictures of key text prompts in the pdf to isolate and cache snapshots of the full pledge report,
    #  then go back through with tesserocr to parse these smaller pieces. This more precise approach should hopefully
    #  save on computation time since the entire pledge report does not need to be parsed.

    print("Converting from pdf to images...")
    pages = convert_from_path(pdf_path, 400)

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
    END_IND = text.index("TOTAL PLEDGES:")
    PLEDGE_COUNT = int(text[END_IND + 8])
    TOTAL_AMT = float(''.join([i for i in text[
        find_nth_containing(text, "Total Amount:", PLEDGE_COUNT+1) + 7] if i not in ['$', ',']]))
    print(PLEDGE_COUNT)
    print(TOTAL_AMT)

    pledges = [Pledge() for _ in range(PLEDGE_COUNT)]
    counter = 0
    nums = 0
    for ind, line in enumerate(text):
        if ind >= END_IND:
            break
        elif pledges[counter].is_complete():
            counter += 1
        if "Payment Type:" in line and '$' in line:
            pledges[counter].cc = 'X' if "Credit Card" in line else ' '
            if '$' in line:
                pledges[counter].amount = float(''.join([i for i in line.split(' ')[2] if i not in ['$', ',']]))
                nums += pledges[counter].amount
                print(pledges[counter].amount)
        elif line == "Total Amount:" and not pledges[counter].is_complete():
            pledges[counter].amount = float(''.join([i for i in text[ind+5] if i not in ['$', ',']]))
            nums += pledges[counter].amount
            print(pledges[counter].amount)
        elif "Campaign Code:" in line:
            pledges[counter].pid = text[ind-2].split(' ')[0]
            pledges[counter].surname = text[ind-2].replace(f'{pledges[counter].pid} ', '').split(',')[0]
        # elif counter>0:  # condition for designation(s) goes here
        #     pass
    print(nums)
    quit()

    pledge_sum = sum([p.amount for p in pledges])
    out_str = '\n'.join([str(p) for p in pledges])
    print(out_str)

    # Printing some diagnostic information to ensure data is correct
    if pledge_sum != TOTAL_AMT:
        print(f"\nIncorrect total amount; Expected {'${:,.2f}'.format(TOTAL_AMT)}, got {'${:,.2f}'.format(pledge_sum)}")
    else:
        print(f"\nTotal amount: {'${:,.2f}'.format(TOTAL_AMT)}")

    pledge_list_count = len(pledges)
    if pledge_list_count != PLEDGE_COUNT:
        print(f"Incorrect pledge count; Expected {TOTAL_AMT}, got {pledge_list_count}\n")
    else:
        print(f"Pledge count: {PLEDGE_COUNT}\n")

    subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    print('Lines copied to keyboard!')


if __name__ == '__main__':
    clear_cache()
    # multiple runs for testing purposes
    for f in ['resources/temp.pdf', 'resources/temp2.pdf', 'resources/temp3.pdf', 'resources/temp4.pdf']:
        main(f)
    clear_cache()
