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


def debug():
    # PID, surname, and CC are 100% working.
    # Designation and amount have some issues; this likely stems from the indexing system.
    text = textract.process('temp.pdf').decode('utf-8').split('\n')
    text = [line.strip() for line in text if len(line)]
    for line in text:
        print(line)


def main():
    print("Started script...")
    text = textract.process('temp.pdf').decode('utf-8').split('\n')
    text = [line.strip() for line in text if len(line)]
    print("Finished reading pdf...")

    total_amt = float(''.join([i for i in text[find_last(text, "Total Amount:") + 1] if i not in ['$', ',']]))
    pledge_count = int(text[text.index("TOTAL PLEDGES:") + 1])
    out_str = ""

    pledges = []
    # initialize pledges list with Pledge objects, find PID and surname, and generate identifying
    # indices for each Pledge object.
    for x in range(pledge_count):
        p = Pledge()
        index = find_nth_containing(text, '     ', x+1)
        index_line = text[index]
        p.index = index
        p.pid = index_line.split('     ')[0]
        p.surname = index_line.split('     ')[1].split(',')[0]
        pledges.append(p)
    # id_counter = 0
    #
    # for x in range(len(text)):
    #     line = text[x]
    #     if id_counter<pledge_count and len(line.split('     ')) == 3:
    #         pledges[id_counter].pid = line.split('     ')[0]
    #         pledges[id_counter].surname = line.split('     ')[1].split(',')[0]
    #         pledges[id_counter].index = x
    #         id_counter += 1

    # loop through all Pledge objects
    for x in range(pledge_count):
        # loop through all lines included in the following range: Pledge.index <= index < NextPledge.index
        upper_index = pledges[x+1].index if x<pledge_count-2 else len(text)-1
        print(upper_index)
        print(x)
        for y in range(pledges[x].index, upper_index):
            line = text[y]
            # find pledge type in scope
            if line == "Pledge Type:":
                pledges[x].cc = "X" if text[y+3] == "Credit Card" else " "
            # find designations in scope
            elif '*' in line:
                des = line
                if any(x not in des for x in ['(', ')']):
                    des += text[y+1]
                pledges[x].add_designation(des)
            # find amount in scope
            elif x>=2 and all(i=='$' for i in [line[0],text[y-1][0],text[y-2][0]]):
                pledges[x].amount = float(''.join([i for i in line if i not in ['$', ',']]))

    pledge_sum = sum([p.amount for p in pledges])
    if pledge_sum != total_amt:
        print(f"Incorrect total amount; Expected {'${:,.2f}'.format(total_amt)}, got {'${:,.2f}'.format(pledge_sum)}")
    else:
        print(f"Total amount: {'${:,.2f}'.format(total_amt)}")

    # pledge_list_count = len([p for p in pledges if p.is_complete()])
    pledge_list_count = len(pledges)
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
    # debug()
