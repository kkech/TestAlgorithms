import sqlalchemy as db
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from jinja2 import Template
from random import seed
from random import randint

class Test:

  def __init__(self):
      self.result = {"result": []}
      print("init")

  def connectToDbAndLoadToPandas(self):
      print("start")
      # engine = db.create_engine('postgresql://test:test@localhost:5432/test')
      engine = db.create_engine('sqlite:////Users/kechagiaskonstantinos/Downloads/uniJob/testsAlgor/datasets.db')
      connection = engine.connect()
      # metadata = db.MetaData()
      # test = db.Table('testtable', metadata, autoload=True, autoload_with=engine)
      # print(test.columns.keys())

      # self.pdResults = pd.read_sql_table("testtable", con=engine)

      self.pdResults = pd.read_sql_table("DATA", con=engine)
      # print(self.pdResults)

      self.pdMetaData = pd.read_sql_table("METADATA", con=engine)
      # print(self.pdMetaData)


  def keepNumericOnly(self, pdData):
    # print(pdData.dtypes)
    pdData = pdData.select_dtypes(include=['number'])
    # print('++++',pdData)
    return pdData

  def clearData(self, pdData):
    for col in pdData.columns:
      print(col)
    pdData = pdData.dropna()
    print(pdData)
    return pdData

  # Flag = 1 -> Generate one json, Flag = 0 -> Generate multiple json
  def generatePcaTests(self, testConf, flag):
    # npTestConf = np.array(testConf)
    jsonList = []
    seed(1)
    # if flag == 1:
    jsonList.append(self.__makeJsonPca(self.pdResults.copy(), testConf))
    # else:
    #   for elem in testConf:
    #     jsonList.append(self.__makeJson(self.pdResults.copy(), elem[0], elem[1]))
    return jsonList

  def generateLrTest(self, testConf, flag):
    jsonList = []
    seed(1)
    tmpMetaData = self.pdMetaData.copy()
    tmpPdResults = self.pdResults.copy()
    tmpMetaData = tmpMetaData[tmpMetaData['isCategorical'] == 1]
    tmpPdResultsY = tmpPdResults[tmpMetaData['code']]
    print(tmpPdResultsY)
    jsonList.append(self.__makeJsonLr(self.pdResults.copy(), tmpPdResultsY, testConf))

    return jsonList

  def __runPCA(self, pdData):
    npTest = pdData.to_numpy()
    print(npTest)
    # print(npTest.shape[1])
    pca = PCA()
    pca.fit(npTest)
    pcaev = pca.explained_variance_
    pcac = pca.components_
    print("===",pcaev)

    # In order to be desc: (-pcaev)
    # arr1inds = (-pcaev).argsort()
    # pcaevSorted = pcaev[arr1inds[::-1]]
    # pcacSorted = pcac[arr1inds[::-1]]

    # Rows Number
    print('Rows = ',npTest.shape[0])
    # Eigenvalues sorted desc
    print('Explained Variance = ', pcaev)
    # Eigenvectors sorted desc
    print('Principal Components = ', pcac)
    return npTest.shape[0], pcaev, pcac

  # def __runLogisticRegression(self, pdData):
  #   return 0

  # def __makeJson(self, pdData, numOfExp, variables):
  #   jsonString = '{"result": ['

  #   t = Template('{ "input": [ { "name": "y", "value": "{{ columns }}" }, { "name": "pathology", "value": "dementia" }, { "name": "dataset", "value": "adni, ppmi, edsd" }, { "name": "filter", "value": "" } ], "output": [ { "name": "n_obs", "value": "{{ rown }}" }, { "name": "eigen_vals", "value": "{{ eigenvalues }}" }, { "name": "eigen_vecs", "value": "{{ eigenvectors }}" } ] }')
  #   for i in range(numOfExp):
  #     tempData = pdData.copy()
  #     while (len(tempData.columns) != variables):
  #       dropColNum = randint(0, len(tempData.columns) - 1)
  #       tempData = tempData.drop(tempData.columns[dropColNum], axis=1)
  #     tempData = self.clearData(tempData)
  #     if tempData.empty:
  #       i = i - 1
  #       continue
  #     columns = "".join(col + "," if ii!=(len(tempData.columns) - 1) else col for ii,col in enumerate(tempData.columns))
  #     rown, pcaev, pcac = self.__runPCA(tempData)
  #     pcaevWithoutLn = np.array_repr(pcaev).replace('\n', '').tolist()
  #     pcacWithoutLn = np.array_repr(pcac).replace('\n', '').tolist()
  #     jsonString = jsonString + t.render(columns=columns, rown=rown, eigenvalues=pcaevWithoutLn, eigenvectors= pcacWithoutLn)
  #     jsonString = jsonString + ","
  #   jsonString = jsonString[:-1]
  #   jsonString = jsonString + ']}'
  #   print(jsonString)
  #   return jsonString


  def __makeJsonPca(self, pdData, testConfig):
    pdData = self.keepNumericOnly(pdData)
    jsonString = '{"result": ['
    t = Template('{ "input": [ { "name": "y", "value": "{{ columns }}" }, { "name": "pathology", "value": "dementia" }, { "name": "dataset", "value": "adni, ppmi, edsd" }, { "name": "filter", "value": "" } ], "output": [ { "name": "n_obs", "value": "{{ rown }}" }, { "name": "eigen_vals", "value": "{{ eigenvalues }}" }, { "name": "eigen_vecs", "value": "{{ eigenvectors }}" } ] }')
    for elem in testConfig:
      numOfExp = elem[0]
      variables = elem[1]
      i = 0
      while (i < numOfExp):
        i = i + 1
        tempData = pdData.copy()
        while (len(tempData.columns) != variables):
          dropColNum = randint(0, len(tempData.columns) - 1)
          tempData = tempData.drop(tempData.columns[dropColNum], axis=1)
        tempData = self.clearData(tempData)
        if tempData.empty:
          i = i - 1
          continue
        columns = "".join(col + "," if ii!=(len(tempData.columns) - 1) else col for ii,col in enumerate(tempData.columns))
        rown, pcaev, pcac = self.__runPCA(tempData)
        # pcaevWithoutLn = np.array_repr(pcaev).replace('\n', '')
        # pcacWithoutLn = np.array_repr(pcac).replace('\n', '')
        pcaevWithoutLn = pcaev.tolist()
        print("---")
        print(pcaev)
        print(pcaev.tolist())
        print("---")
        pcacWithoutLn = pcac.tolist()
        jsonString = jsonString + t.render(columns=columns, rown=rown, eigenvalues=pcaevWithoutLn, eigenvectors= pcacWithoutLn)
        jsonString = jsonString + ","
    jsonString = jsonString[:-1]
    jsonString = jsonString + ']}'
    print(jsonString)
    return jsonString
      
  def __makeJsonLr(self, pdData, pdDataY, testConfig):
    pdData = self.keepNumericOnly(pdData)
    jsonString = '{"result": ['
    t = Template('{ "input": [{ "name": "x", "label": "x", "desc": "A list of variables from database. The variable should be Real, Integer. It cannot be empty", "type": "column", "columnValuesSQLType": "real, integer", "columnValuesIsCategorical": "false", "value": "{{ columns }}", "valueNotBlank": true, "valueMultiple": true, "valueType": "string" }, { "name": "y", "label": "y", "desc": "A single variable from database. The variable should be Categorical with only two categories (i.e. Boolean). It cannot be empty.", "type": "column", "columnValuesSQLType": "text, integer", "columnValuesIsCategorical": "true", "value": "{{yColumns}}", "valueNotBlank": true, "valueMultiple": false, "valueType": "string" }, { "name": "pathology", "label": "pathology", "desc": "The name of the pathology that the dataset belongs to.", "type": "pathology", "value": "dementia", "valueNotBlank": true, "valueMultiple": false, "valueType": "string" }, { "name": "dataset", "label": "dataset", "desc": "It contains the names of one or more datasets, in which the algorithm will be executed. It cannot be empty", "type": "dataset", "value": "adni", "valueNotBlank": true, "valueMultiple": true, "valueType": "string" }, { "name": "filter", "label": "filter", "desc": "", "type": "filter", "value": "", "valueNotBlank": false, "valueMultiple": true, "valueType": "string" } ], "output": [{ "name": "params", "value": "{{params}}" }] }')
    for elem in testConfig:
      numOfExp = elem[0]
      variables = elem[1]
      i = 0
      while (i < numOfExp):
        i = i + 1
        print("****",i)
        tempData = pdData.copy()
        tempDataY = pdDataY.copy()
        while (len(tempData.columns) != variables):
          dropColNum = randint(0, len(tempData.columns) - 1)
          tempData = tempData.drop(tempData.columns[dropColNum], axis=1)
        keepColNum = randint(0, len(tempDataY.columns) - 1)
        tempDataY = tempDataY.iloc[:, [keepColNum]]
        print("++++")
        print(tempDataY)
        tempData[tempDataY.columns[0]] = tempDataY
        print(tempData)
        print("----")
        tmp = self.pdMetaData[self.pdMetaData['code'] == tempDataY.columns[0]]
        print(tmp['enumerations'])
        enumerations = tmp['enumerations'].to_string(index=False).split(",")
        enumerations = [x.strip(' ') for x in enumerations]
        print(enumerations)
        while (len(enumerations) != 2):
          dropIndex = randint(0, len(enumerations) - 1)
          del enumerations[dropIndex]
        print("||||")
        print(enumerations)
        print("||||")
        tempData = tempData.loc[tempData[tempDataY.columns[0]].isin(enumerations)]
        print(tempData)
        print("||||----")

        tempData = self.clearData(tempData)
        print(tempData)

        print("!!!!!", tempData.nunique()[-1:][0] == 2)

        if (tempData.empty) or (tempData.nunique()[-1:][0] != 2):
          i = i - 1
          print("****",i)
          print('EMPTY')
          continue
        print('PASS')

        # -2 because last column is Y
        columns = "".join(col + "," if ii!=(len(tempData.columns) - 2) else col for ii,col in enumerate(tempData.columns))
        enumString = ','.join(enumerations)

        # -----
        # keepColNum = randint(0, len(pdDataY.columns) - 1)
        # print(pdDataY.iloc[:, [keepColNum]])
        # -----
        y = tempData.iloc[:,-1]
        X = tempData.iloc[:, :-1]
        
        clf = LogisticRegression(random_state=0, solver='newton-cg', penalty='none').fit(X, y)
        print("====")
        print(clf.get_params())
        print("====")
        jsonString = jsonString + t.render(columns=columns, yColumns=enumString, params=clf.get_params())
        jsonString = jsonString + ","
    jsonString = jsonString[:-1]
    jsonString = jsonString + ']}'
    print(jsonString)
    return jsonString
test = Test()
test.connectToDbAndLoadToPandas()
resultList = test.generateLrTest([[20,2]],1)
myfile = open('testLr.txt', 'w')
for elem in resultList:
  myfile.write(elem)
  myfile.write("\n")
myfile.close()


# resultList = test.generatePcaTests([[20,2], [30,1]],1)
# myfile = open('test.txt', 'w')
# for elem in resultList:
#   myfile.write(elem)
#   myfile.write("\n")
# myfile.close()
