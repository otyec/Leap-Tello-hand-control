import re

def stateToDict(string):
    string = string.rstrip()
    list=re.split(r'[:;]', string)
    
    dict = {}
    i=0
    
    while i < len(list)-2:
      name = list[i]
      value = list[i+1]
      dict[name]=value
      i = i+2

    return dict