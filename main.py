import subprocess
import textract
from typing import List


class Pledge:
    def __init__(self):
        # 'X' if the pledge was on a credit card and ' ' if it was not.
        self.cc: str = ''
        # A string representation of the prospect's PID.
        self.pid: str = ''
        # The prospect's surname.
        self.surname: str = ''
        # A list of the designation or designations for the pledge.
        self.designation: List[str] = []
        # A float representation of the pledge amount.
        self.amount: float = -1.0
        # The index in the list of text rows that marks the start of the pledge information.
        self.index: int = -1

    def __str__(self):
        return f"Pledge object\nCC: {self.cc}\nSurname: {self.surname}\nPID: {self.pid}\n" \
               f"Amount: {self.amount}\nDesignation(s): {', '.join(self.designation)}\nIndex: {self.index}\n"

    def is_complete(self) -> bool:
        """Checks to see whether all fields of the Pledge object are filled."""
        return '' not in [self.cc, self.surname] and -1 not in [self.pid, int(self.amount), self.index] \
               and len(self.designation) != 0

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


def find_pledge_by_index(pledges, text_len, ind) -> int:
    """Returns the list index Pledge in the provided list that matches the provided index if present and -1 otherwise"""
    if ind > text_len-1:
        return -1
    counter = 0
    for p in pledges:
        if counter == len(pledges)-1:
            return counter
        if p.index <= ind < pledges[counter+1].index:
            return counter
        counter += 1


def main():
    print("Started script...")
    text = textract.process('temp.pdf').decode('utf-8').split('\n')
    text = [line.strip() for line in text if len(line)]
    print("Finished reading pdf...")

    total_amt = float(''.join([i for i in text[find_last(text, "Total Amount:") + 1] if i not in ['$', ',']]))
    pledge_count = int(text[text.index("TOTAL PLEDGES:") + 1])

    pledges = []
    for x in range(pledge_count):
        p = Pledge()
        p.cc = "X" if text[find_nth(text, "Pledge Type:", x+1)+3] == "Credit Card" else " "
        pledges.append(p)

    out_str = ""

    amt_counter = 0
    id_counter = 0
    curr_index = 0
    for line in text:
        # print(line)
        if amt_counter<pledge_count and curr_index>=2 and \
                all(x=='$' for x in [line[0],text[curr_index-1][0],text[curr_index-2][0]]):
            pledges[amt_counter].amount = float(''.join([i for i in line if i not in ['$', ',']]))
            amt_counter += 1
        elif id_counter<pledge_count and len(line.split('     ')) == 3:
            pledges[id_counter].pid = line.split('     ')[0]
            pledges[id_counter].surname = line.split('     ')[1].split(',')[0]
            pledges[id_counter].index = curr_index
            id_counter += 1
        curr_index += 1

    curr_index = 0
    for line in text:
        if '*' in line:
            des = line
            if any(x not in des for x in ['(', ')']):
                des += text[curr_index + 1]
            pledges[find_pledge_by_index(pledges, len(text), curr_index)].add_designation(des)
        curr_index += 1

    pledge_sum = sum([p.amount for p in pledges])
    if pledge_sum != total_amt:
        print(f"Incorrect total amount; Expected {'${:,.2f}'.format(total_amt)}, got {'${:,.2f}'.format(pledge_sum)}")
    else:
        print(f"Total amount: {'${:,.2f}'.format(total_amt)}")

    pledge_list_count = len([p for p in pledges if p.is_complete()])
    if pledge_list_count != pledge_count:
        print(f"Incorrect pledge count; Expected {pledge_count}, got {pledge_list_count}")
    else:
        print(f"Pledge count: {pledge_count}")

    for p in pledges:
        out_line = ','.join([str(p.pid), p.surname, '/'.join(p.designation), str(p.amount), p.cc])
        print(out_line)
        out_str += out_line + '\n'

    subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    print('Lines copied to keyboard!')


if __name__ == "__main__":
    main()
