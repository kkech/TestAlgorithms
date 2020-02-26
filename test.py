import sqlalchemy as db
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from jinja2 import Template
from random import seed
from random import randint

class Test:
  """
    blueprint for car
  """

  def __init__(self):
      self.result = {"result": []}
      print("init")

  def connectToDbAndLoadToPandas(self):
      print("start")
      engine = db.create_engine('postgresql://test:test@localhost:5432/test')
      connection = engine.connect()
      # metadata = db.MetaData()
      # test = db.Table('testtable', metadata, autoload=True, autoload_with=engine)
      # print(test.columns.keys())
      self.pdResults = pd.read_sql_table("testtable", con=engine)
      print(self.pdResults)

  def clearData(self):
    for col in self.pdResults.columns: 
      print(col)
    self.pdClearResults = self.pdResults.dropna()
    print(self.pdClearResults)

  def generateTests(self, testConf):
    # npTestConf = np.array(testConf)
    jsonList = []
    seed(1)
    for elem in testConf:
      jsonList.append(self.__makeJson(self.pdClearResults.copy(), elem[0], elem[1]))
    return jsonList
  
  def __runPCA(self, pdData):
    npTest = pdData.to_numpy()
    print(npTest)
    # print(npTest.shape[1])
    pca = PCA()
    pca.fit(npTest)
    pcaev = pca.explained_variance_
    pcac = pca.components_

    # In order to be desc: (-pcaev)
    arr1inds = (-pcaev).argsort()
    pcaevSorted = pcaev[arr1inds[::-1]]
    pcacSorted = pcac[arr1inds[::-1]]

    # Rows Number
    print('Rows = ',npTest.shape[0])
    self.rown = npTest.shape[0]
    # Eigenvalues sorted desc
    print('Explained Variance = ', pcaevSorted)
    self.pcaevSorted = pcaevSorted
    # Eigenvectors sorted desc
    print('Principal Components = ', pcacSorted)
    self.pcacSorted = pcacSorted
    return npTest.shape[0], pcaevSorted, pcacSorted


  def __makeJson(self, pdData, numOfExp, variables):
    jsonString = '{"result": ['

    t = Template('{ "input": [ { "name": "y", "value": "{{ columns }}" }, { "name": "pathology", "value": "dementia" }, { "name": "dataset", "value": "adni, ppmi, edsd" }, { "name": "filter", "value": "" } ], "output": [ { "name": "n_obs", "value": "{{ rown }}" }, { "name": "eigen_vals", "value": "{{ eigenvalues }}" }, { "name": "eigen_vecs", "value": "{{ eigenvectors }}" } ] }')
    for i in range(numOfExp):
      tempData = pdData.copy()
      while (len(tempData.columns) != variables):
        dropColNum = randint(0, len(tempData.columns) - 1)
        tempData = tempData.drop(tempData.columns[dropColNum], axis=1)
      columns = "".join(col + "," if ii!=(len(tempData.columns) - 1) else col for ii,col in enumerate(tempData.columns))
      rown, pcaevSorted, pcacSorted = self.__runPCA(tempData)
      pcaevSortedWithoutLn = np.array_repr(pcaevSorted).replace('\n', '')
      pcacSortedWithoutLn = np.array_repr(pcacSorted).replace('\n', '')
      jsonString = jsonString + t.render(columns=columns, rown=rown, eigenvalues=pcaevSortedWithoutLn, eigenvectors= pcacSortedWithoutLn)
      jsonString = jsonString + ","
    jsonString = jsonString[:-1]
    jsonString = jsonString + ']}'
    print(jsonString)
    return jsonString


