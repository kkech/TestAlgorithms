from test import Test

test = Test()
test.connectToDbAndLoadToPandas()
test.clearData()
resultList = test.generateTests([[20,2], [30,1], [50, 3]])
myfile = open('test.txt', 'w')
for elem in resultList:
  myfile.write(elem)
  myfile.write("\n")
myfile.close()