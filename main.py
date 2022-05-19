import os
import re
import subprocess
import sys
import textract
from typing import List


class Pledge:
    def __init__(self):
        # 'X' if the pledge was on a credit card and a space character (' ') if it was not.
        self.cc: str = ''
        # A string representation of the prospect's PID.
        self.pid: str = ''
        # The prospect's surname.
        self.surname: str = ''
        # A list containing the designation or designations for the pledge.
        self.designation: List[str] = []
        # A float representation of the pledge amount.
        self.amount: float = 0.0
        # The index in the list of text rows that marks the start of the pledge information.
        self.index: int = -1

    def __str__(self):
        if self.is_complete():
            return ','.join([str(self.pid), self.surname, '/'.join(self.designation),
                             '${:.2f}'.format(self.amount), self.cc])
        return ','.join([str(self.pid), self.surname, '?', '?', self.cc])

    def is_complete(self) -> bool:
        """Checks to see whether all fields of the Pledge object have been filled."""
        return '' not in [self.cc, self.surname] and -1 not in [self.pid, self.index] \
               and 0 not in [len(self.designation), self.amount]

    def add_designation(self, designation):
        """Appends the desired element to the self.designation List."""
        self.designation.append(designation)


def find_last(elts, element) -> int:
    """Returns the index of the last time the element is found in the given list if present and -1 otherwise."""
    if element in elts:
        return max(i for i, item in enumerate(elts) if item == element)
    return -1


def find_nth(elts, element, n) -> int:
    """Returns the index of the nth time the element is found in the given list if present and -1 otherwise."""
    counter = 0
    index = 0
    for x in elts:
        if x == element:
            counter += 1
        if counter == n:
            return index
        index += 1
    return -1


def find_nth_containing(elts, phrase, n) -> int:
    """Returns the index of the nth term containing the given phrase if present and -1 otherwise."""
    counter = 0
    index = 0
    for x in elts:
        if phrase in x:
            counter += 1
        if counter == n:
            return index
        index += 1
    return -1


def main():
    path = '/Users/nolan/Downloads/'

    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    pdf_path = max(paths, key=os.path.getctime)
    print(pdf_path)

    if len(sys.argv) > 2:
        print("This program only accepts a single argument!")
        quit()
    elif len(sys.argv) == 2:
        pdf_path = path + sys.argv[1] + '.pdf'

    text = [line.strip() for line in textract.process(pdf_path).decode('utf -8').split('\n')]
    text = [line for line in text if len(line)]

    regex_pattern = r'[78]\d{8} [a-zA-z -]+, [a-zA-z -]+'
    index_lines = [i for i, line in enumerate(text) if re.search(regex_pattern, line)]

    total_amt = float(''.join([i for i in text[find_last(text, "Total Amount:") + 1] if i not in ['$', ',']]))
    pledge_count_index = text.index("TOTAL PLEDGES:")
    pledge_count = int(text[pledge_count_index + 1])

    pledges = []

    # initialize pledges list with Pledge objects, find PID and surname, and generate
    # identifying indices for each object.
    for x in range(pledge_count):
        p = Pledge()
        index = index_lines[x]
        split_index_line = text[index].split(' ')
        p.index = index
        p.pid = split_index_line[0].strip()
        p.surname = split_index_line[1].strip()[:-1]
        pledges.append(p)

    # loop through all Pledge objects
    for index, pledge in enumerate(pledges):
        # loop through all lines included in the following range: Pledge.index <= index < NextPledge.index
        lower_index = pledge.index if index > 0 else 0
        upper_index = pledges[index + 1].index if index < (pledge_count - 1) else pledge_count_index
        for inner_idx, line in enumerate(text[lower_index:upper_index], start=lower_index):
            # find pledge type in scope
            if pledge.cc == '':
                if "Credit Card" in line:
                    pledge.cc = "X"
                elif "Check" in line:
                    pledge.cc = " "
                elif inner_idx == (upper_index - 1):
                    pledge.cc = "?"
            # find designation(s) in scope
            elif '*' in line:
                des = line
                if any(x not in des for x in ['(', ')']):
                    des += text[inner_idx + 1]
                if text[inner_idx - 1] != "Designation Name" and '*' not in text[inner_idx - 1] \
                        and text[inner_idx - 2] + text[inner_idx - 1] not in pledge.designation:
                    des = text[inner_idx - 1] + ' ' + des
                pledge.add_designation(des)
            # find amount in scope
            elif inner_idx >= 2 and pledge.amount == 0 \
                    and "Total Amount:" in line:
                pledge.amount = float(''.join([i for i in text[inner_idx+1] if i not in ['$', ',']]))
        # If the current Pledge object does not have a designation, clear the last object's designation and
        # amount in addition to this object's amount so that the appropriate designations and amounts may be
        # filled in manually.
        if index and not pledge.designation:
            pledge.amount = 0.0
            pledges[index-1].amount = 0.0
            pledges[index-1].designation = []

    pledge_sum = sum([p.amount for p in pledges])
    out_str = '\n'.join([str(p) for p in pledges])
    print(out_str)

    # Printing some diagnostic information to ensure data is correct
    if pledge_sum != total_amt:
        print(f"\nIncorrect total amount; Expected {'${:,.2f}'.format(total_amt)}, got {'${:,.2f}'.format(pledge_sum)}")
    else:
        print(f"\nTotal amount: {'${:,.2f}'.format(total_amt)}")

    pledge_list_count = len(pledges)
    if pledge_list_count != pledge_count:
        print(f"Incorrect pledge count; Expected {pledge_count}, got {pledge_list_count}\n")
    else:
        print(f"Pledge count: {pledge_count}\n")

    subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    print('Lines copied to keyboard!')


if __name__ == "__main__":
    main()
