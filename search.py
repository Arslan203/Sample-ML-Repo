import random
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class Document:
    def __init__(self, title, text, t_v):
        # можете здесь какие-нибудь свои поля подобавлять
        self.title = title
        self.text = text
        self.title_vec = t_v

    def format(self, query):
        # возвращает пару тайтл-текст, отформатированную под запрос
        return [self.title, self.text + ' ...']

index = {}
documents = []


def build_index():
    df = pd.read_csv('dataframe.csv')
    with open('vecs.pickle', 'rb') as f:
        vecs = pickle.load(f)
    for i in range(df.shape[0]):
        v = np.zeros([300])
        c = 0
        # высчитываем вектор title
        for j in df.iloc[i]['title'].lower().replace('.', ' ').split():
            try:
                v += vecs[j]
                c += 1
            except KeyError:
                None
        v = v / c
        documents.append(Document(df.iloc[i]['title'], df.iloc[i]['body'], v))
        for word in set((documents[i].title.replace('.', ' ') + ' ' + documents[i].text).lower().split()):
            if word not in index:
                index[word] = []
            index[word].append(i)


def score(query, document):
  count_word = []
  for j in query.lower().split():
    tmp = 0
    for i in (document.title + ' ' + document.text).replace('.', ' ').lower().split():
      if j == i:
        tmp += 1
    count_word.append(tmp)
  query_vect = np.zeros([300])
  c = 0
  for j in query.lower().split():
    try:
      query_vect += vecs[j]
      c += 1
    except KeyError:
      None
  if c != 0:
    query_vect = query_vect / c
  print(count_word)
  print(document.tf_vect)
  return cosine_similarity(query_vect.reshape(1, -1), document.title_vec.reshape(1, -1))[0][0] * 10 + np.array(document.tf_vect).sum() * 5 + np.array(count_word).sum()


def retrieve(query):
    tf_idf_vect = []
    candidates = []
    ind = []
    for i in query.lower().split():
        ind.append([0, i])
    i = 0
    while i < len(ind):
        if ind[i][1] not in set(index.keys()):
            ind.pop(i)
        else:
            i += 1
    while len(candidates) < 10 and len(ind) > 0:
        Out_of_range = False
        while len(candidates) < 50 and not (Out_of_range):
            candidate = True
            m = index[ind[0][1]][ind[0][0]]
            cur = 0
            for k, j in enumerate(ind):
                if index[j[1]][j[0]] != m:
                    candidate = False
                if index[j[1]][j[0]] < m:
                    m = index[j[1]][j[0]]
                    cur = k
            if candidate:
                candidates.append(m)
                tf_idf_vect.append(documents[m].title + ' ' + documents[m].text)
            ind[cur][0] += 1
            if len(index[ind[cur][1]]) == ind[cur][0]:
                Out_of_range = True
        for i in ind:
            i[0] = 0
        if len(ind) != 0:
            ind.pop()

    tf_vectorizer = TfidfVectorizer()
    tf_idf_vect = tf_vectorizer.fit_transform(tf_idf_vect)
    for k, i in enumerate(candidates):
        documents[i].tf_vect = [(tf_idf_vect[k, tf_vectorizer.vocabulary_[j]]) for j in query.lower().split()]
    return candidates
