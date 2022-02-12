import regex as re
import textract
import subprocess

# TODO: Yow and Carmichael not included in temp.pdf file; figure out why! Consider refining
#  data collection to be more precise.

# Tsai got CC & designation overwritten with info from Yow.
# Campbell and Castro have no changes from Carmichael.

text = textract.process('/Users/nolan/Downloads/temp2.pdf').decode('utf-8').split('\n')
text = [line for line in text if len(line)]
pledges = []
out = ''

counter = 0
pledge = {'CC': '', 'Designation': '', 'Amount': '', 'PID': '', 'Surname': ''}
for line in text:
    # debugging lines
    print(line)
    # continue
    print(pledge)

    if '' not in pledge.values():
        pledges.append(pledge)
        pledge = {'CC': '', 'Designation': '', 'Amount': '', 'PID': '', 'Surname': ''}

    if pledge['PID'] == '' and pledge['Surname'] == '' and len(line.split('     ')):
        reg_pid = re.sub("[^0-9]", "", line.split('     ')[0])
        if len(reg_pid) == 9 and reg_pid[0] == '7':
            pledge['PID'] = reg_pid
            print(line)
            pledge['Surname'] = line.split('     ')[1].split(',')[0]
            print(pledge['PID'])
            print(pledge['Surname'])
    elif pledge['Amount'] == '' and line[0] == '$' and text[counter-1][0] == '$' and text[counter-2][0] == '$':
        pledge['Amount'] = line
        print(pledge['Amount'])
    elif pledge['CC'] == '' and line == "Pledge Type:":
        pledge['CC'] = 'X' if text[counter+3] == "Credit Card" else ' '
        print(pledge['CC'])
    elif pledge['Designation'] == '' and line == "Designation Name":
        pledge['Designation'] = text[counter+1]
        if any(x not in pledge['Designation'] for x in ['(', ')', '*']):
            pledge['Designation'] += text[counter+2]
            print(pledge['Designation'])
    counter += 1

for p in pledges:
    out_line = ','.join([p["PID"], p["Surname"], p["Designation"], p["Amount"], p["CC"]])
    print(out_line)
    out += out_line + '\n'


print('\n' + str(len(pledges)) + ' total pledges.\n')

subprocess.run("pbcopy", universal_newlines=True, input=out)
print('Lines copied to keyboard!')
