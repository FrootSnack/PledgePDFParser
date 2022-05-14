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
        return ','.join([str(self.pid), self.surname, '?', '?', '?'])

    def is_complete(self) -> bool:
        """Checks to see whether all fields of the Pledge object have been filled."""
        return '' not in [self.cc, self.surname] and -1 not in [self.pid, self.index] \
               and 0 not in [len(self.designation), self.amount]

    def add_designation(self, designation):
        """Appends the desired element to the self.designation List."""
        self.designation.append(designation)
