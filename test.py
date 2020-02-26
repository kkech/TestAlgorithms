import sqlalchemy as db
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from jinja2 import Template
from random import seed
from random import randint

class Test:

  def __init__(self):
      self.result = {"result": []}

  def connectToDbAndLoadToPandas(self):
      engine = db.create_engine('sqlite:////Users/kechagiaskonstantinos/Downloads/uniJob/testsAlgor/datasets.db')
      connection = engine.connect()
      self.pdResults = pd.read_sql_table("DATA", con=engine)
      self.pdResults = self.keepNumericOnly(self.pdResults)

  def keepNumericOnly(self, pdData):
    pdData = pdData.select_dtypes(include=['number'])
    return pdData

  def clearData(self, pdData):
    pdData = pdData.dropna()
    return pdData

  # Flag = 1 -> Generate one json, Flag = 0 -> Generate multiple json
  def generateTests(self, testConf, flag):
    jsonList = []
    seed(1)
    if flag == 1:
      jsonList.append(self.__makeJsonProd(self.pdResults.copy(), testConf))
    else:
      for elem in testConf:
        jsonList.append(self.__makeJson(self.pdResults.copy(), elem[0], elem[1]))
    return jsonList

  def __runPCA(self, pdData):
    npTest = pdData.to_numpy()
    
    pca = PCA()
    pca.fit(npTest)
    pcaev = pca.explained_variance_
    pcac = pca.components_
    arr1inds = (-pcaev).argsort()
    pcaevSorted = pcaev[arr1inds[::-1]]
    pcacSorted = pcac[arr1inds[::-1]]
    self.rown = npTest.shape[0]
    self.pcaevSorted = pcaevSorted
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
      tempData = self.clearData(tempData)
      if tempData.empty:
        i = i - 1
        continue
      columns = "".join(col + "," if ii!=(len(tempData.columns) - 1) else col for ii,col in enumerate(tempData.columns))
      rown, pcaevSorted, pcacSorted = self.__runPCA(tempData)
      pcaevSortedWithoutLn = np.array_repr(pcaevSorted).replace('\n', '')
      pcacSortedWithoutLn = np.array_repr(pcacSorted).replace('\n', '')
      jsonString = jsonString + t.render(columns=columns, rown=rown, eigenvalues=pcaevSortedWithoutLn, eigenvectors= pcacSortedWithoutLn)
      jsonString = jsonString + ","
    jsonString = jsonString[:-1]
    jsonString = jsonString + ']}'
    return jsonString


  def __makeJsonProd(self, pdData, testConfig):
    jsonString = '{"result": ['

    t = Template('{ "input": [ { "name": "y", "value": "{{ columns }}" }, { "name": "pathology", "value": "dementia" }, { "name": "dataset", "value": "adni, ppmi, edsd" }, { "name": "filter", "value": "" } ], "output": [ { "name": "n_obs", "value": "{{ rown }}" }, { "name": "eigen_vals", "value": "{{ eigenvalues }}" }, { "name": "eigen_vecs", "value": "{{ eigenvectors }}" } ] }')
    for elem in testConfig:
      numOfExp = elem[0]
      variables = elem[1]
      for i in range(numOfExp):
        tempData = pdData.copy()
        while (len(tempData.columns) != variables):
          dropColNum = randint(0, len(tempData.columns) - 1)
          tempData = tempData.drop(tempData.columns[dropColNum], axis=1)
        tempData = self.clearData(tempData)
        if tempData.empty:
          i = i - 1
          continue
        columns = "".join(col + "," if ii!=(len(tempData.columns) - 1) else col for ii,col in enumerate(tempData.columns))
        rown, pcaevSorted, pcacSorted = self.__runPCA(tempData)
        pcaevSortedWithoutLn = np.array_repr(pcaevSorted).replace('\n', '')
        pcacSortedWithoutLn = np.array_repr(pcacSorted).replace('\n', '')
        jsonString = jsonString + t.render(columns=columns, rown=rown, eigenvalues=pcaevSortedWithoutLn, eigenvectors= pcacSortedWithoutLn)
        jsonString = jsonString + ","
    jsonString = jsonString[:-1]
    jsonString = jsonString + ']}'
    return jsonString
