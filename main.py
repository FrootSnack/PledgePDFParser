import subprocess
import textract
from typing import List

# TODO: Properly implement Pledge.last_index parameter.

# TODO: Solve discrepancies in designation. Current problem is weird ordering (see Drake & Elenez).
#  Everything else appears to be solved in the temp.pdf document.

# TODO: Solve discrepancies in amount

# TODO: Check whether CC issue is fixed using other files


class Pledge:
    def __init__(self):
        # 'X' if the pledge was on a credit card and ' ' if it was not.
        self.cc: str = ''
        # A string representation of the prospect's PID.
        self.pid: str = ''
        # The prospect's surname.
        self.surname: str = ''
        # The prospect's first name. This is not printed but is used to extract other information.
        self.name: str = ''
        # A list containing the designation or designations for the pledge.
        self.designation: List[str] = []
        # A float representation of the pledge amount.
        self.amount: float = 0.0
        # The index in the list of text rows that marks the start of the pledge information.
        self.index: int = -1
        # The last index that has been used to extract data for this Pledge. Useful if other Pledge objects
        # have data before their index value.
        self.last_index: int = -1

    def __str__(self):
        return f"Pledge object\nCC: {self.cc}\nSurname: {self.surname}\nPID: {self.pid}\n" \
               f"Amount: {self.amount}\nDesignation(s): {', '.join(self.designation)}\nIndex: {self.index}\n"

    # TODO: remove this method if it is not used in the final product
    def is_complete(self) -> bool:
        """Checks to see whether all fields of the Pledge object have been filled."""
        return '' not in [self.cc, self.surname] and -1 not in [self.pid, self.index] \
               and len(self.designation) != 0 and self.amount != 0.0

    def add_designation(self, designation):
        """Appends the desired element to the self.designation List."""
        self.designation.append(designation)

    def clear_all(self):
        """Resets all data fields to their default value."""
        self.cc = ''
        self.pid = ''
        self.surname = ''
        self.name = ''
        self.designation = []
        self.amount = 0.0
        self.index = -1
        self.last_index = -1


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


# TODO: remove this function if it isn't used in the finished product
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
        p.name = index_line.split('     ')[1].split(',')[1].strip()
        p.last_index = index if index > p.last_index else p.last_index
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
                pledges[x].last_index = y if y > pledges[x].last_index else pledges[x].last_index
            # find designation(s) in scope
            elif '*' in line:
                des = line
                if any(x not in des for x in ['(', ')']):
                    des += text[y+1]
                if text[y-1] != "Designation Name" and '*' not in text[y-1] \
                        and text[y-2]+text[y-1] not in pledges[x].designation:
                    des = text[y-1] + ' ' + des
                pledges[x].add_designation(des)
                pledges[x].last_index = y if y > pledges[x].last_index else pledges[x].last_index
            # find amount in scope
            elif y>=2 and pledges[x].amount == 0 \
                    and all(i=='$' for i in [line[0],text[y-1][0],text[y-2][0]]) and text[y-3]!='Average':
                pledges[x].amount = float(''.join([i for i in line if i not in ['$', ',']]))
                pledges[x].last_index = y if y > pledges[x].last_index else pledges[x].last_index
        # If the current Pledge object does not have a designation, clear the last object's designation and
        # amount in addition to this object's amount so that the appropriate designations and amounts may be
        # filled in manually.
        if x>0 and not pledges[x].designation:
            pledges[x].amount = 0.0
            pledges[x-1].amount = 0.0
            pledges[x-1].designation = []

    # # Loop through unfinished Pledge objects to assign appropriate designation(s)
    # for x in range(len(pledges)):
    #     # Skip all objects with a non-empty designation List
    #     if pledges[x].designation:
    #         continue
    #     print('\n')
    #     print(pledges[x].surname)
    #     lower_index = pledges[x-1].last_index if x > 0 else 0
    #     upper_index = pledges[x+1].index if x < pledge_count - 1 else text.index("TOTAL PLEDGES:")
    #     for y in range(lower_index, upper_index):
    #         line = text[y]
    #         if line == "From" and text[y+1] == pledges[x].name:
    #             for z in range(pledges[x].index, y):
    #                 print(text[z])
    #                 if '*' in text[z]:
    #                     des = text[z]
    #                     if any(x not in des for x in ['(', ')']):
    #                         des += text[y+1]
    #                     if text[z-1] != "Designation Name" and '*' not in text[z-1] \
    #                             and text[z-2]+text[z-1] not in pledges[x].designation:
    #                         des = text[z-1] + ' ' + des
    #                     pledges[x].add_designation(des)
    #                     pledges[x].last_index = z if z > pledges[x].last_index else pledges[x].last_index

    for p in pledges:
        out_line = ','.join([str(p.pid), p.surname, '/'.join(p.designation), str(p.amount), p.cc])
        print(out_line)
        out_str += out_line + '\n'

    # Printing some diagnostic information to ensure data is correct
    pledge_sum = sum([p.amount for p in pledges])
    if pledge_sum != total_amt:
        print(
            f"\nIncorrect total amount; Expected {'${:,.2f}'.format(total_amt)}, got {'${:,.2f}'.format(pledge_sum)}")
    else:
        print(f"\nTotal amount: {'${:,.2f}'.format(total_amt)}")

    # pledge_list_count = len([p for p in pledges if p.is_complete()])
    pledge_list_count = len(pledges)
    if pledge_list_count != pledge_count:
        print(f"Incorrect pledge count; Expected {pledge_count}, got {pledge_list_count}\n")
    else:
        print(f"Pledge count: {pledge_count}\n")

    subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    print('Lines copied to keyboard!')


if __name__ == "__main__":
    main('temp3.pdf')
    # debug('temp2.pdf')
