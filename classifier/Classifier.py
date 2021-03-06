#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
from sklearn import metrics
from sklearn.feature_extraction import DictVectorizer, FeatureHasher
from sklearn.feature_extraction.text import HashingVectorizer,TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
from sklearn.ensemble import BaggingClassifier,ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier,GradientBoostingClassifier,VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.decomposition import PCA,TruncatedSVD
import Levenshtein
import numpy
import math
import collections
#from merge import Merge
#from dep import Dep
import cPickle as pickle
import json
import traceback
#should not use the class right now,i need to change the method _process_data to let the test data can get answer accurately
class Classifier:
	def setIden(self,identify):
		self.identify=identify
		if identify == 'muqin':
			self.newwords2=[u"妈妈",u"母亲"]#muqin
		elif identify == 'fuqin':
			self.newwords2=[u"爸爸",u"父亲"]#fuqin
		elif identify == 'erzi':
			self.newwords2=[u"儿子"]#erzi
		elif identify == 'nver':
			self.newwords2=[u"女儿"]#nver
		elif identify == 'nvyou':
			self.newwords2=[u"女友",u"女朋友"]#nvyou
		elif identify == 'nanyou':
			self.newwords2=[u"男友",u"男朋友"]#nanyou
		elif identify == 'zhangfu':
			self.newwords2=[u"丈夫",u"老公",u"夫妇"]#zhangfu
		elif identify == 'qizi':
			self.newwords2=[u"妻子",u"老婆",u"夫人",u"夫妇"]#qizi
		print self.newwords2[0].encode('utf-8')
		import cPickle as pickle
		from sklearn.externals import joblib
		strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_norm.txt'
		#strs = 'classifier/train_data/muqin_VotingClassifier_norm.txt'
		print strs
		self.normalizer=pickle.load(open(strs, 'rb'))
		strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_logic_dep.train'
		print strs
		self.clf = joblib.load(strs)
		print self.clf
		from InterClassifier import InterClassifier
		self.ic = InterClassifier(self.genre,self.newwords2,self.stop)
		
	#genre:dict n_tuple n_dict line
	#vec:hashingvec featurehash dictvec
	#type:gaussiannb lr
	def __init__(self,test=True,genre='line',vec='hashingvec',type='lr',identify='muqin'):
		file = open('stopwords.txt','rb')
		line = file.readline()
		self.stop=[]
		while line:
			self.stop.append(line.strip('\r\n').strip('\n'))
			line = file.readline()
		self.genre = genre
		self.vec = vec
		self.type = type
		self.test = test
		self.identify=identify
		if identify == 'muqin':
			self.newwords2=[u"\u5988\u5988",u"\u6bcd\u4eb2"]#muqin
		elif identify == 'fuqin':
			self.newwords2=[u"\u7238\u7238",u"\u7236\u4eb2"]#fuqin
		elif identify == 'erzi':
			self.newwords2=[u"\u513f\u5b50"]#erzi
		elif identify == 'nver':
			self.newwords2=[u"\u5973\u513f"]#nver
		elif identify == 'nvyou':
			self.newwords2=[u"\u5973\u670b\u53cb",u"\u5973\u53cb"]#nvyou
		elif identify == 'nanyou':
			self.newwords2=[u"\u7537\u670b\u53cb",u"\u7537\u53cb"]#nanyou
		elif identify == 'zhangfu':
			self.newwords2=[u"\u8001\u516c",u"\u4e08\u592b",u"\u592b\u5987"]#zhangfu
		elif identify == 'qizi':
			self.newwords2=[u"\u8001\u5a46",u"\u592b\u4eba",u"\u59bb\u5b50",u"\u592b\u5987"]#qizi
		print self.newwords2[0].encode('utf-8')
		if test:
			import cPickle as pickle
			from sklearn.externals import joblib
			#TODO
			strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_norm.txt'
			#strs = 'classifier/train_data/muqin_VotingClassifier_norm.txt'
			print strs
			self.normalizer=pickle.load(open(strs, 'rb'))
			strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_logic_dep.train'
			print strs
			self.clf = joblib.load(strs)
			print self.clf
		from InterClassifier import InterClassifier
		self.ic = InterClassifier(genre,self.newwords2,self.stop)
		import re
		self.de = re.compile(u"[\u4e00-\u9fa5]")
		self.relation = {u'fuqin':('PERSON','PERSON'),u'erzi':('PERSON','PERSON'),u'nver':('PERSON','PERSON'),u'nvyou':('PERSON','PERSON'),u'nanyou':('PERSON','PERSON'),u'muqin':('PERSON','PERSON'),u'emma':('PERSON','PERSON'),u'zhangfu':('PERSON','PERSON'),u'qizi':('PERSON','PERSON'),u'\u5973\u53cb':('PERSON','PERSON'),u'\u5973\u513f':('PERSON','PERSON'),u'\u59bb\u5b50':('PERSON','PERSON'),u'\u4e08\u592b':('PERSON','PERSON'),u'\u524d\u592b':('PERSON','PERSON'),u'\u7236\u4eb2':('PERSON','PERSON'),u'\u8eab\u9ad8':('PERSON','HEIGHT'),u'\u751f\u65e5':('PERSON','DATE'),u'\u64ad\u51fa\u65f6\u95f4':('FILM','TIME'),u'\u4e3b\u9898\u66f2':('FILM','MUSIC')}
		self.speci = ["、",",","，","&"]
		self.speci2 = ["-",":","》","并","从","图","、",",","(",")","【","】","-","|","‖","☆ ","与","/","及","；","为","也","被","，","&","·","_","的","等","]","”","吗","#","《","吧","在","是","?","？","很","：","说","都","饰","和","而","里","（","[","“","）","."]
		self.biaodian = [u"\u3001",",",u"\uff0c",".",u"\u3002","|",u"\uff1b","_",u"\uff1a",":",u"\u201d",u"\u201c"]
		#self.biaodian = ["、",",","，",".","。","|","；","_","：",":","”","“"]
		pass

	def _process_data_indri(self,lines_info,newwords,tags=None,htmls=None):
		if self.vec == 'union':
			return self.ic._process_data_indri(lines_info,newwords,tags,htmls)
		else:
			return self.ic._process_data_indri_old(lines_info,newwords,tags,htmls)

	def _vectorize_HashingVectorizer(self,words):
		vec = HashingVectorizer(n_features=2**20)
		vectorized = vec.transform(words)
		return vectorized

	def _vectorize_hash(self,words):
		if self.genre == 'n_tuple':
			vec = FeatureHasher(n_features=2**10,input_type='pair')
		elif self.genre == 'n_dict':
			vec = FeatureHasher(n_features=2**10)
		vectorized = vec.transform(words)
		#vectorized = preprocessing.scale(vectorized)
		#vectorized = preprocessing.normalize(vectorized)
		return vectorized
	
	#the train data and test data must be in the same dimension 
	def _vectorize_dict(self,words):
		vec =  DictVectorizer()
		pos_vectorized = vec.fit_transform(words)
		return pos_vectorized

	def _vectorize_union(self,words):
		#TODO
		strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_tfidf.txt'
		#strs = 'classifier/train_data/muqin_VotingClassifier_tfidf.txt'
		print strs
		if self.test:
			tv=pickle.load(open(strs, 'rb'))
			vocabulary = tv.vocabulary_
			strs=None
		else:
			vocabulary = None
		pipeline = Pipeline([
			('SentenceDep', SentenceDepExtractor()),
			('union', FeatureUnion(
				transformer_list=[
					('line', Pipeline([
						('selector', ItemSelector(key='line')),
						('dict',  DictVectorizer()),
					])),
					('dep', Pipeline([
						('selector', ItemSelector(key='dep')),
						('tfidf', FeatureHasher(n_features=2**7,input_type='dict')),
					])),
					('sentence', Pipeline([
						('selector', ItemSelector(key='sentence')),
						('tfidf', SaveTfidfVectorizer(strs,vocabulary = vocabulary,stop_words=self.stop)),
						('best', TruncatedSVD(n_components=100)),
					])),
				],
				# weight components in FeatureUnion
				transformer_weights={
					'line' : 0.4,
					'sentence': 0.1,
					'dep': 0.5,
				},
			)),
		])
		return pipeline.fit_transform(words)

	def _train_clf(self,vec,tag):
		if self.type =='gaussiannb':
			clf = GaussianNB()
		elif self.type =='lr':
			#clf = LogisticRegression(multi_class='multinomial',solver='lbfgs')
			clf = LogisticRegression(solver='lbfgs')
		elif self.type =='svc':
			clf = SVC(probability=True)#default with 'rbf'  
		elif self.type == 'BaggingClassifier':
			clf = BaggingClassifier(KNeighborsClassifier())
		elif self.type =='KNeighborsClassifier':
			clf = KNeighborsClassifier()
		elif self.type =='RandomForestClassifier':
			clf =RandomForestClassifier()
		elif self.type=='AdaBoostClassifier':
			clf = AdaBoostClassifier()
		elif self.type=='DecisionTreeClassifier':
			clf = DecisionTreeClassifier()
		elif self.type=='ExtraTreesClassifier':
			clf = ExtraTreesClassifier()
		elif self.type=='GradientBoostingClassifier':
			clf = GradientBoostingClassifier()
		elif self.type=='VotingClassifier':
			clf1 = DecisionTreeClassifier()
			clf2 = RandomForestClassifier()
			clf3 = LogisticRegression(solver='lbfgs')
			clf4 = GradientBoostingClassifier()
			clf5 = AdaBoostClassifier()
			#clf3 = GaussianNB()
			#clf = VotingClassifier(estimators=[('dt', clf1), ('rf', clf2), ('gnb', clf3)], voting='soft',weights=[3,3,1])
			clf = VotingClassifier(estimators=[('dt', clf1), ('rf', clf2),('lr',clf3),('gb',clf4),('ac',clf5)], voting='soft',weights=[2,2,3,3,3])
			#clf = VotingClassifier(estimators=[('rf', clf2),('lr',clf3),('gb',clf4),('ac',clf5)], voting='soft',weights=[2,3,3,3])
		print 'calu'
		if self.type =='gaussiannb' or self.type=='GradientBoostingClassifier':
			clf.fit(vec.toarray(), numpy.asarray(tag))
		else:
			clf.fit(vec, numpy.asarray(tag))
		#clf.fit(vec.toarray(), numpy.asarray(tag))
		print 'calu end'
		return clf

	def train_using_process(self,p,words):
		print 'start vec'
		if self.vec =='hashingvec':
			vec = self._vectorize_HashingVectorizer(words)
		elif self.vec =='featurehash':
			vec = self._vectorize_hash(words)
		elif self.vec =='dictvec':
			vec = self._vectorize_dict(words)
		elif self.vec == 'union':
			vec = self._vectorize_union(words)
		print 'vec successfully!'
		normalizer = preprocessing.Normalizer().fit(vec)
		strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_norm.txt'
		print strs
		pickle.dump(normalizer,open(strs, 'wb'))
		vec = normalizer.transform(vec)
		#strs = 'classifier/'+self.identify+'_'+self.type+'_union.txt'
		#print strs
		#pickle.dump(vec,open(strs, 'wb'))
		print len(words)
		print len(p)
		return self._train_clf(vec,p)
	
	def train_using_process_(self,p,words):
		from sklearn.externals import joblib
		vec = joblib.load('classifier/muqin_VotingClassifier_union.txt')
		print len(p)
		return self._train_clf(vec,p)

	def classifier_using_process(self,s,p,words,_seg,_ner,clf,htmls,an,deps):
		if self.vec =='hashingvec':
			vec = self._vectorize_HashingVectorizer(words)
		elif self.vec =='featurehash':
			vec = self._vectorize_hash(words)
		elif self.vec =='dictvec':
			vec = self._vectorize_dict(words)
		elif self.vec == 'union':
			vec = self._vectorize_union(words)
		vec = self.normalizer.transform(vec)   
		check = False
		try:
			pred = clf.predict(vec.toarray())
		except:
			traceback.print_exc()  
			check = True
		dec = clf.predict_proba(vec.toarray())
		#dec = clf.decision_function(vec.toarray())
		m_s=[]
		m_p=[]
		m_seg=[]
		m_ner=[]
		m_dep=[]
		for i in xrange(len(p)):
			#print 'test info : '+s[i].encode('utf-8')+' '+an+' '+pred[i]+' '+htmls[i]+' '+''.join(_seg[i]).encode('utf-8')
			#print dec[i]
			#if p[i] == pred[i] and dec[i]>25.0:
			#if p[i] == pred[i] and dec[i][1]>0.5:
			if p[i]==pred[i] or check:
				#print s[i].encode('utf-8')+' '+str(i+1)+' '+pred[i]+' '+''.join(_seg[i]).encode('utf-8')
				m_s.append(s[i])
				m_p.append(p[i])
				m_seg.append(_seg[i])
				m_ner.append(_ner[i])
				m_dep.append(deps[i])
			else:
				pass
		return (m_s,m_p,m_seg,m_ner,m_dep)
		
	def classifier_get_score(self,s,p,words,_seg,clf):
		if self.vec =='hashingvec':
			vec = self._vectorize_HashingVectorizer(words)
		elif self.vec =='featurehash':
			vec = self._vectorize_hash(words)
		elif self.vec =='dictvec':
			vec = self._vectorize_dict(words)
		elif self.vec == 'union':
			vec = self._vectorize_union(words)
		vec = self.normalizer.transform(vec)
		pred = clf.predict(vec.toarray())
		score = accuracy_score(p, pred)
		#for i in xrange(len(p)):
		#	print s[i].encode('utf-8')+' '+str(i+1)+' '+pred[i]+' '+''.join(_seg[i]).encode('utf-8')
		return (score,len(pred))

	def _train(self,lines_info,newwords,tags):
		(s,p,word,_seg,_ner) = self._process_data_indri(lines_info,newwords,tags=tags)
		#import cPickle as pickle
		#strs = 'classifier/train_tag_'+self.identify+'_dep.txt'
		#print strs
		#f = open(strs, 'wb') 
		#strs = 'classifier/train_hash_'+self.identify+'_dep.txt'
		#print strs
		#f2 = open(strs, 'wb')
		#pickle.dump(word,f2)
		#f2.close()
		#pickle.dump(p,f)
		#f.close()
		#quit(0)
		#TODO
		return self.train_using_process(p,word)

	def _test(self,lines_info,newwords,tags,htmls,an):
		#print 'Process Data start'
		(s,p,words,_seg,_ner,htmls,deps) = self._process_data_indri(lines_info,newwords,tags=tags,htmls=htmls)
		if len(words)<2:
			return []
		#print 'Classifier start'
		(s,p,_seg,_ner,deps) = self.classifier_using_process(s,p,words,_seg,_ner,self.clf,htmls,an,deps)
		if len(p)<2:
			return []
		list=self.statistics(s,p,_seg,_ner,deps)
		if len(list)==0:
			print 'len list ==0'
			return []
		return list

	def test_train_indri(self,l,lines_info):
		lines =[]
		tags =[]
		newwords=[]
		for line in l:
			try:
				line = line.split('\t')
				tags.append(line[1])
				newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
				lines.append(line[3].strip())
			except Exception,e:
				traceback.print_exc()
		clf = self._train(lines_info,newwords,tags=tags)
		from sklearn.externals import joblib
		strs = 'classifier/train_data/'+self.identify+'_'+self.type+'_logic_dep.train'
		print strs
		joblib.dump(clf,strs)
		print clf

	def test_test_indri(self,_lines,lines_info):
		lines=[]
		tags=[]
		newwords=[]
		htmls=[]
		an = '' 
		for line in _lines:
		     try:
			line = line.split('\t')
			if len(line)<4:
				#print 'read wrong ('+str(len(line))+'):'+'\t'.join(line)
				continue
			tags.append(line[1])
			an = line[2]
			htmls.append(line[4].strip())
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
			if line[3].strip()!='':
				lines.append(line[3].strip())
		     except :
			     info=sys.exc_info() 
		      	     print 'read wrong (except):'+'\t'.join(line)
		return self._test(lines_info,newwords,tags=tags,htmls=htmls,an=an)

	def test_verify_indri(self,_lines,lines_info):
		#just count
		#using classifier
		tags=[]
		newwords=[]
		for line in _lines:
		     try:
			line = line.split('\t')
			if len(line)<4:
				#print 'read wrong ('+str(len(line))+'):'+'\t'.join(line)
				continue
			tags.append(line[1])
			newwords.append((line[0],(self.relation[line[1].decode('utf-8')])[0]))
		     except:
			info=sys.exc_info()
		#print 'Process Data start'
		(s,p,words,_seg,_ner) = self._process_data_indri(lines_info,newwords,tags=tags)
		if len(words)<2:
			return (0,0)
		#print 'Classifier start'
		return self.classifier_get_score(s,p,words,_seg,self.clf)

	def _semi_Levenshtein(self,lines):
		strs=[]
		lines = lines.split('\t')
		for id in xrange(len(lines)):
			l = lines[id]
			for s in strs:
				ratio = Levenshtein.ratio(s,l)
				if ratio<0.6:
					return True
			strs.append(l)
		return False

	#count the answer of a relation
	def statistics(self,newwords,tags,segs,ners,deps):
		s=newwords[0]
		p=tags[0]
		answer=[]
		fromline=[]
		dict = collections.OrderedDict()
		for i in xrange(len(tags)):
			tag = tags[i]
			seg = segs[i]
			ner = ners[i]
			#dep = deps[i]
			index_p=-1
			for nn in self.newwords2:
				if nn in seg:
					index_p = seg.index(nn)
					break
				else:
					#for ds in xrange(len(seg)):
					#	if seg[ds].find(nn):
					#		index_p = ds
					#	else:
							index_p=-1
			if index_p == -1:
				print ' '.join(seg).encode('utf-8')
				print 'None P '
				continue
			if newwords[i] in seg:
				index_s = seg.index(newwords[i])
			else:
				#for ds in xrange(len(seg)):
				#	if seg[ds].find(newwords[i]):
				#		index_s = ds
				#	else:
				#		index_s = -1
				#if index_s == -1:
					print ' '.join(seg).encode('utf-8')
					print 'None S'
					continue
			#print ' '.join(seg).encode('utf-8')+str(index_p)+','+str(index_s)
			#print ' '.join(dep).encode('utf-8')
			_a = []
			lianxu = 0
			dict_dis = collections.OrderedDict()
			fromline.append(''.join(seg))
			for id in xrange(len(seg)):
				if tags is not None:
					if ner[id] == (self.relation[tag.decode('utf-8')])[1]:
						ll = len(self.de.findall(seg[id]))
						if ll==0:
							ll=len(seg[id])
						if (seg[id] != newwords[i]) and (seg[id] not in _a)  and (ll>1) and seg[id].isdigit()==False:
							if id<len(seg)-1 and len(seg[id])<3 and len(seg[id+1])==1 and (seg[id+1].encode('utf-8') not in self.speci2):
								maybe = seg[id]+seg[id+1]
							else:
								maybe=''
							try:
								distance = round(0.1/(math.fabs(id-index_p)+math.fabs(id-index_s)),2)
								if id-index_p==1 and id-index_s==2:
									distance+=2
								elif id-index_p==1 and ner[id-2] != (self.relation[tag.decode('utf-8')])[1]:
									distance+=1
								if id>index_p:
									pnw=id
									pt=index_p
								else:
									pnw=index_p
									pt=id
								ss = seg[pt:pnw]
								if len(ss)!=0 and len(set(ss).intersection(set(self.biaodian)))==0:
									distance+=0.1
								#if dep[id].split('_')[1]==index_p+1:
								#	print 'dep info'
								#	distance+=1
								#elif dep[id].split('_')[1]==index_s+1:
								#	print 'dep info'
								#	distance+=0.5
							except :
								traceback.print_exc()
								#print 'math error'+newwords[i].encode('utf-8')+','+tag.encode('utf-8')+','+seg[id].encode('utf-8')+str(math.fabs(id-index_p))+' '+str(math.fabs(id-index_s))
								continue
							#print newwords[i].encode('utf-8')+','+tag.encode('utf-8')+','+seg[id].encode('utf-8')+','+str(distance+0.15)
							#if maybe!='':
								#print 'add '+newwords[i].encode('utf-8')+','+tag.encode('utf-8')+','+maybe.encode('utf-8')+','+str(distance+0.15)
							if seg[id] in answer:
								dict[seg[id]]+=distance+0.15001
							else:
								dict[seg[id]]=distance+0.15001
							if maybe!='':
								if maybe in answer:
									dict[maybe]+=distance+0.15001
								else:
									dict[maybe]=distance+0.15001
							lianxu += 1
							dict_dis[seg[id]]=distance+0.15001
							_a.append(seg[id])
							answer.append(seg[id])
							if maybe!='':
								dict_dis[maybe]=distance+0.15001
								_a.append(maybe)
								answer.append(maybe)
					else:
						if seg[id].encode('utf-8') in self.speci:
							continue
						if lianxu>=3:
							b=''
							while lianxu>0:
								asa = answer.pop()
								dict[asa]-=dict_dis[asa]
								if b != asa[1:2]:
									lianxu -= 1
								b=asa
						lianxu = 0
		dict= sorted(dict.iteritems(), key=lambda d:d[1], reverse = True)
		list=[]
		try :
			max = dict[0][1]
			if max<=0:
				return []
		except:
			print 'classifier 492 error'
			return []
		top=3
		for v in dict:
			times=(v[1]*100-int(v[1]*100))*1000
			if int(times) == 0 :
				continue
			if (top>0 and int(times)>1) or (v[1]/times>0.16 and int(times)>5):
				if v[1] != max :
					top-=1
					max = top
				strs = s+'\t'+p+'\t'+v[0]+'\t'+str(v[1])+'\t'+str(int(times))
			else:
				continue
			lll=''
			for line in fromline:
				if line.find(v[0]) != -1:
					#times+=1
					lll += '\t'+line
			strs+=lll
			list.append(strs)
			#list.append(lll)
		return list


if __name__ == '__main__':
	c = Classifier(test=False,genre='n_tuple')
	c.test_train()
	#c.test()
from sklearn.base import BaseEstimator, TransformerMixin

class SentenceDepExtractor(BaseEstimator, TransformerMixin):
	def fit(self, x, y=None):
		return self
	def transform(self, posts):
		features = numpy.recarray(shape=(len(posts),),dtype=[('sentence', object), ('line',object),('dep', object)])
		for i,dep in enumerate(posts):
			features['dep'][i] = dep[1]
			features['line'][i] = dep[0]
			features['sentence'][i] = dep[2]
		print 'SentenceDepExtractor'
		return features

class ItemSelector(BaseEstimator, TransformerMixin):
	def __init__(self, key):
		self.key = key

	def fit(self, x, y=None):
		return self

	def transform(self, data_dict):
		print self.key
		return data_dict[self.key]

class SaveTfidfVectorizer(TfidfVectorizer):
	def __init__(self,key=None, input='content', encoding='utf-8',decode_error='strict', strip_accents=None, lowercase=True,preprocessor=None, tokenizer=None, analyzer='word',stop_words=None, token_pattern=r"(?u)\b\w\w+\b",ngram_range=(1, 1), max_df=1.0, min_df=1,max_features=None, vocabulary=None, binary=False,dtype=numpy.int64, norm='l2', use_idf=True, smooth_idf=True,sublinear_tf=False):
		super(SaveTfidfVectorizer,self).__init__(input=input, encoding=encoding, decode_error=decode_error,strip_accents=strip_accents, lowercase=lowercase,preprocessor=preprocessor, tokenizer=tokenizer, analyzer=analyzer,stop_words=stop_words, token_pattern=token_pattern,ngram_range=ngram_range, max_df=max_df, min_df=min_df,max_features=max_features, vocabulary=vocabulary, binary=binary,dtype=dtype,norm=norm, use_idf=use_idf, smooth_idf=smooth_idf,sublinear_tf=sublinear_tf)
		self.key = key
		
	def fit(self, raw_documents, y=None):
		return super(SaveTfidfVectorizer, self).fit(raw_documents)

	def fit_transform(self, raw_documents, y=None):
		clf = super(SaveTfidfVectorizer, self).fit_transform(raw_documents)
		if self.key is not None:
			pickle.dump(super(SaveTfidfVectorizer,self),open(self.key, 'wb'))
			print 'saved in fit_transform'
		return clf

	def transform(self, raw_documents, copy=True):
		clf = super(SaveTfidfVectorizer, self).transform(raw_documents)
		if self.key is not None:
			pickle.dump(super(SaveTfidfVectorizer,self),open(self.key, 'wb'))
			print 'saved in transform'
		return clf
