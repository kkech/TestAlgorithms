from test import Test

test = Test()
test.connectToDbAndLoadToPandas()
resultList = test.generateTests([[25,5], [25,10], [25, 15], [25,20]],1)
myfile = open('test.txt', 'w')
for elem in resultList:
  myfile.write(elem)
  myfile.write("\n")
myfile.close()