import random

class Contact:

    def __init__(self, info):
        self.contact_name = info['contact_name']
        self.contact_position = info['contact_position']
        self.email = info['email']
        self.phone = info['phone']
        self.id = None

    def __eq__(self, other):
        if isinstance(self, other):
            return (
                    self.contact_name == other.contact_name and
                    self.contact_position == other.contact_position and 
                    self.email == other.email and 
                    self.phone == other.phone
                    )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        start = 1
        end = 1000
        key = random.randint(start, end)
        self.id = key
        return key
        

