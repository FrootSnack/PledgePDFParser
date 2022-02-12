from typing import List

import regex as re
import textract
import subprocess

# Implemented: Amount, total $, pledge count, CC y/n, PID, surname, index
# To be implemented:  designation(s)


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


def find_pledge_by_index(pledges, ind) -> int:
    """Returns the list index Pledge in the provided list that matches the provided index if present and -1 otherwise"""
    for x in range(len(pledges)):
        if x == len(pledges)-1:
            return len(pledges)-1
        if pledges[x].index <= ind < pledges[x + 1].index:
            return x
    return -1


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
        p.amount = float(text[find_nth(text, "Total Amount:", x+1)+3])
        p.cc = "X" if text[find_nth(text, "Pledge Type:", x+1)+3] == "Credit Card" else " "
        pledges.append(p)

    out_str = ""

    for t in text:
        print(t)
    exit()

    # new loop
    amt_counter = 0
    id_counter = 0
    curr_index = 0
    for line in text:
        if amt_counter<pledge_count and all(x=='$' for x in [line[0],text[curr_index-1][0],text[curr_index-2][0]]):
            pledges[amt_counter].amount = float(''.join([i for i in line if i not in ['$', ',']]))
            print(pledges[amt_counter].amount)
            amt_counter += 1
        elif id_counter<pledge_count and len(line.split('     ')) == 3:
            pledges[id_counter].pid = line.split('     ')[0]
            pledges[id_counter].surname = line.split('     ')[1].split(',')[0]
            pledges[id_counter].index = curr_index
            id_counter += 1
        elif '*' in line:
            pledges[find_pledge_by_index(pledges, curr_index)].add_designation(line)
        curr_index += 1
    exit()



    # counter = 0
    # pledge = {'CC': '', 'Designation': '', 'Amount': '', 'PID': '', 'Surname': ''}

    # old below
    # for line in text:
    #     # debugging lines
    #     print(line)
    #     continue
    #     print(pledge)
    #
    #     if '' not in pledge.values():
    #         pledges.append(pledge)
    #         pledge = {'CC': '', 'Designation': '', 'Amount': '', 'PID': '', 'Surname': ''}
    #
    #     if pledge['PID'] == '' and pledge['Surname'] == '' and len(line.split('     ')):
    #         reg_pid = re.sub("[^0-9]", "", line.split('     ')[0])
    #         if len(reg_pid) == 9 and reg_pid[0] == '7':
    #             pledge['PID'] = reg_pid
    #             print(line)
    #             pledge['Surname'] = line.split('     ')[1].split(',')[0]
    #             print(pledge['PID'])
    #             print(pledge['Surname'])
    #     elif pledge['Amount'] == '' and line[0] == '$' and text[counter - 1][0] == '$' and text[counter - 2][0] == '$':
    #         pledge['Amount'] = line
    #         print(pledge['Amount'])
    #     elif pledge['CC'] == '' and line == "Pledge Type:":
    #         pledge['CC'] = 'X' if text[counter + 3] == "Credit Card" else ' '
    #         print(pledge['CC'])
    #     elif pledge['Designation'] == '' and line == "Designation Name":
    #         pledge['Designation'] = text[counter + 1]
    #         if any(x not in pledge['Designation'] for x in ['(', ')', '*']):
    #             pledge['Designation'] += text[counter + 2]
    #             print(pledge['Designation'])
    #     counter += 1

    # new below
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

    # old below
    # for p in pledges:
    #     out_line = ','.join([p["PID"], p["Surname"], p["Designation"], p["Amount"], p["CC"]])
    #     print(out_line)
    #     out_str += out_line + '\n'

    # print('\n' + str(len(pledges)) + ' total pledges.\n')

    # new below
    for p in pledges:
        out_line = ','.join([str(p.pid), p.surname, p.designation, str(p.amount), p.cc])
        print(out_line)
        out_str += out_line + '\n'

    subprocess.run("pbcopy", universal_newlines=True, input=out_str)
    print('Lines copied to keyboard!')


if __name__ == "__main__":
    main()
