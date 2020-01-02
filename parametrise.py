#Reads data.txt and dataTrimmed.txt and decides which message chunks to map to parameters.

with open('data.txt', 'r') as d:
    data = d.readlines()

dataList = []
for item in data:
    dataList.append(eval(item))

with open('dataTrimmed.txt', 'r') as dt:
    dataT = dt.readlines()

dataTList = []
for item in dataT:
    dataTList.append(eval(item))

#First check for numbers and grab the 3 with the largest bin size and range.
toParam = []
toAdd = ['n','n','n']
for i in range(len(dataList)):
    if dataList[i]['isNumber'] and dataList[i]['range'] != 'N/A':
       for j in range(len(toAdd)):
            if toAdd[j] == 'n' or len(dataList[i]['bin boundaries']) > len(dataList[toAdd[j]]['bin boundaries']):
                toAdd.insert(j, i)
                toAdd.pop(-1)
                break 
            elif dataList[i]['range'] > dataList[toAdd[j]]['range']:
                toAdd.insert(j, i)
                toAdd.pop(-1)
                break

for item in toAdd:
    if item != 'n':
        toParam.append(item)

#Then choose top 3 rated from non-numbers (or less if list is shorter)
toAdd = ['n','n','n'] #Stored top 3 positions as placeholder string for now.
for i in range(len(dataTList)):
    if dataTList[i]['isNumber'] == False:
        for j in range(len(toAdd)):
            if toAdd[j] == 'n' or dataTList[i]['rating'] > dataTList[toAdd[j]]['rating']:
                toAdd.insert(j, i)
                toAdd.pop(-1)
                #print(toAdd)
                break

for item in toAdd:
    if item != 'n' and len(toParam) <= 2:
        toParam.append(item)

print(toParam)
f = open("key.txt", "w+")
f.write(str(toParam))
f.close()