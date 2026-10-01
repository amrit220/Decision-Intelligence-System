def valstr(text):
    while True:
        try:
            value = input(text)
            if value.strip() == "":
                raise ValueError
            if not value[0].isalpha():
                print("Please Enter a valid string starting with (A-Z,a-z)")
                continue
            if len(value) > 60:
                raise ValueError    
            return value
        except ValueError:
             print("INVALID String, Please enter a Valid String Under 60 Characters: ")
            
def valfac(text):
    while True:
        try:
            value = int(input(text))
            if value < 0 or value > 10:
                print("please enter between (0-10). ")
                continue
            return value    
        except ValueError:
             print("INVALID INPUT, Please enter a Number: ")

def valopt(text):

    while True:
        try:
            value = int(input(text))

            if value < 2 or value > 6:
                raise ValueError

            return value

        except ValueError:
            print("Please enter a valid number of options (2-6).")