import os

file1 = open('function_list', 'r') 
Lines = file1.readlines() 

for line in Lines:
    newFunction  = line.split(' ')
    cmd = 'find . -type f -name "*.py" -print0 | xargs -0 sed -i \'s/'+newFunction[0]+'/'+newFunction[1].rstrip()+'/g\''
    os.system(cmd)
    print(cmd)
    print(newFunction[0]+' is now '+newFunction[1])

