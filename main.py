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
        # A list containing the designation or designations for the pledge.
        self.designation: List[str] = []
        # A float representation of the pledge amount.
        self.amount: float = 0.0
        # The index in the list of text rows that marks the start of the pledge information.
        self.index: int = -1

    def __str__(self):
        return f"Pledge object\nCC: {self.cc}\nSurname: {self.surname}\nPID: {self.pid}\n" \
               f"Amount: {self.amount}\nDesignation(s): {', '.join(self.designation)}\nIndex: {self.index}\n"

    def is_complete(self) -> bool:
        """Checks to see whether all fields of the Pledge object have been filled."""
        return '' not in [self.cc, self.surname] and -1 not in [self.pid, self.index] \
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


def debug(pdf_path='temp.pdf'):
    # PID, surname, and CC are 100% working.
    # Designation and amount have some issues; this likely stems from the indexing system.
    text = textract.process(pdf_path).decode('utf-8').split('\n')
    text = [line.strip() for line in text if len(line)]
    out_str = ''
    for line in text:
        out_str += line+'\n'
    subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    print('Lines copied to keyboard!')


def main(pdf_path='temp.pdf'):
    print("Started script...")
    text = textract.process(pdf_path).decode('utf-8').split('\n')
    text = [line.strip() for line in text if len(line)]
    print("Finished reading pdf...\n")

    total_amt = float(''.join([i for i in text[find_last(text, "Total Amount:") + 1] if i not in ['$', ',']]))
    pledge_count = int(text[text.index("TOTAL PLEDGES:") + 1])
    out_str = ""

    pledges = []
    # initialize pledges list with Pledge objects, find PID and surname, and generate
    # identifying indices for each object.
    for x in range(pledge_count):
        p = Pledge()
        index = find_nth_containing(text, '     ', x+1)
        index_line = text[index]
        p.index = index
        p.pid = index_line.split('     ')[0].strip()
        p.surname = index_line.split('     ')[1].split(',')[0].strip()
        pledges.append(p)

    # loop through all Pledge objects
    for x in range(pledge_count):
        # loop through all lines included in the following range: Pledge.index <= index < NextPledge.index
        lower_index = pledges[x].index if x>0 else 0
        upper_index = pledges[x+1].index if x<pledge_count-1 else text.index("TOTAL PLEDGES:")
        for y in range(lower_index, upper_index):
            line = text[y]
            # find pledge type in scope
            if line == "Specified Pledge" and pledges[x].cc == '':
                pledge_type = text[y+1]
                if pledge_type == "Credit Card":
                    pledges[x].cc = "X"
                elif pledge_type == "Check":
                    pledges[x].cc = " "
                else:
                    pledges[x].cc = "?"
            # find designation(s) in scope
            elif '*' in line:
                des = line
                if any(x not in des for x in ['(', ')']):
                    des += text[y+1]
                if text[y-1] != "Designation Name" and '*' not in text[y-1] \
                        and text[y-2]+text[y-1] not in pledges[x].designation:
                    des = text[y-1] + ' ' + des
                pledges[x].add_designation(des)
            # find amount in scope
            elif y>=2 and pledges[x].amount == 0 \
                    and all(i=='$' for i in [line[0],text[y-1][0],text[y-2][0]]) and text[y-3]!='Average':
                pledges[x].amount = float(''.join([i for i in line if i not in ['$', ',']]))
        # If the current Pledge object does not have a designation, clear the last object's designation and
        # amount in addition to this object's amount so that the appropriate designations and amounts may be
        # filled in manually.
        if x>0 and not pledges[x].designation:
            pledges[x].amount = 0.0
            pledges[x-1].amount = 0.0
            pledges[x-1].designation = []

    for p in pledges:
        out_line = ','.join([str(p.pid), p.surname, '?', '?', '?'])
        if p.is_complete():
            out_line = ','.join([str(p.pid), p.surname, '/'.join(p.designation), '${:,.2f}'.format(p.amount), p.cc])
        print(out_line)
        out_str += out_line + '\n'

    # Printing some diagnostic information to ensure data is correct
    pledge_sum = sum([p.amount for p in pledges])
    if pledge_sum != total_amt:
        print(
            f"\nIncorrect total amount; Expected {'${:,.2f}'.format(total_amt)}, got {'${:,.2f}'.format(pledge_sum)}")
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
    main('/Users/nolan/Downloads/2-17_pledges.pdf')
    # debug('temp4.pdf')
