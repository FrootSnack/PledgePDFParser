import regex as re
import textract
import subprocess


# TODO: Yow and Carmichael not included in temp.pdf file; figure out why! Consider refining
#  data collection to be more precise.

# Tsai got CC & designation overwritten with info from Yow.
# Campbell and Castro have no changes from Carmichael.

class Pledge:
    def __init__(self):
        self.cc = None
        self.pid = None
        self.surname = None
        self.designation = None
        self.amount = None

    def check_complete(self) -> bool:
        if None not in [self.cc, self.pid, self.surname, self.designation, self.amount]:
            return True
        return False


def find_last(elts=[], element=None) -> int:
    """Returns the index of the last time the element is found in the given list if present and -1 otherwise."""
    if element in elts:
        return max(i for i, item in enumerate(elts) if item==element)
    return -1


def find_nth(elts=[], element=None, n=1) -> int:
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


def main():
    text = textract.process('/Users/nolan/Downloads/temp2.pdf').decode('utf-8').split('\n')
    text = [line.strip() for line in text if len(line)]

    total_amt = float(''.join([i for i in text[find_last(text, "Total Amount:")+1] if i not in ['$', ',']]))
    pledge_count = int(text[text.index("TOTAL PLEDGES:")+1])

    pledges = []
    for x in range(pledge_count):
        p = Pledge()
        pledges.append(p)

    out = ''

    # for t in text:
    #     print(t)
    # exit()

    # new loop
    amt_counter = 0
    curr_index = 0
    for line in text:
        if amt_counter < pledge_count and line[0] == '$' and text[curr_index - 1][0] == '$' and text[curr_index - 2][0] == '$':
            pledges[amt_counter].amount = float(''.join([i for i in line if i not in ['$', ',']]))
            print(pledges[amt_counter].amount)
            amt_counter += 1
        curr_index += 1
    exit()
    for x in range(pledge_count):
        print(text[find_nth(text, "Total Amount:", x+1)+3])
        print()
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
        print(f"Total Amount: {'${:,.2f}'.format(total_amt)}")

    pledge_list_count = len(pledges)
    if pledge_list_count != pledge_count:
        print(f"Incorrect pledge count; Expected {pledge_count}, got {pledge_list_count}")
    else:
        print(f"Pledge Count: {pledge_count}")

    # old below
    # for p in pledges:
    #     out_line = ','.join([p["PID"], p["Surname"], p["Designation"], p["Amount"], p["CC"]])
    #     print(out_line)
    #     out += out_line + '\n'

    # print('\n' + str(len(pledges)) + ' total pledges.\n')

    subprocess.run("pbcopy", universal_newlines=True, input=out)
    print('Lines copied to keyboard!')


if __name__ == "__main__":
    main()
