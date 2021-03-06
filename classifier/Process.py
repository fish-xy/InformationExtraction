#!/usr/bin/env python
#-*-coding:utf-8-*- 
import sys
sys.path.append("..")
import Classifier
import traceback  
import Levenshtein
import commands
import json
import re
#from dep import TextSim
class Process:
	def setIden(self,iden):
		self.c.setIden(iden)
	def __init__(self,test=False):
		#self.t = TextSim()
		self.rels = {}
		self.rels["erzi"] = [u"儿子"]    
		self.rels["nver"] = [u"女儿"]
		self.rels["nanyou"] = [u"男友",u"男朋友"]
		self.rels["nvyou"] = [u"女友",u"女朋友"]
		self.rels["muqin"] = [u"妈妈",u"母亲"]
		self.rels["fuqin"] = [u"爸爸",u"父亲"]
		self.rels["qizi"] = [u"妻子",u"老婆",u"夫人",u"夫妇"]
		self.rels["zhangfu"] = [u"丈夫",u"老公",u"夫妇"]
		#TODO 添加新关系时，需要加入新的关系引导词  self.rels["xinguanxi"]=[u"xinguanxi"] 
		self.q = re.compile(r'\\')
		self.p = re.compile('<[^>]+>') 
		self.b = re.compile('(http|ftp|https)?(:\/\/)?([\w\-_]+\.)+([\w\-:_]+/)([\w\-\.,@^=%&amp;:/~\+#]+)?')
		self.test = test
		if test is True:
			self.c = Classifier.Classifier(type='GradientBoostingClassifier',vec='featurehash',genre='n_dict',identify='muqin')
		pass
	
	def _semi_without(self,lines,lines_info,htmls):
		strs=[]
		strs_info=[]
		strs_htmls=[]
		for i in xrange(len(lines)):
			l = lines[i]
			l = self.p.sub("", l)
			l = self.b.sub("", l)
			l = l.strip('\n').lstrip('”').lstrip('。').lstrip('.').lstrip('，').lstrip(',')
			if len(l)>400 or len(l)<5:
				continue
			strs.append(l)
			strs_info.append(lines_info[i])
			strs_htmls.append(htmls[i])
		return (strs,strs_info,strs_htmls)

	def _semi_Levenshtein(self,lines,lines_info):
		strs=[]
		strs_info=[]
		for id in xrange(len(lines)):
			l = lines[id]
			line = l.split('\t')
			l = line[3]
			check=True
                        #l = self.p.sub("", l)
                        #l = self.b.sub("", l)
			#l = l.strip('\n')
			#l = l.decode('utf-8').lstrip(u'\u201d').lstrip(u'\u3002').lstrip('.').lstrip(u'\uff0c').lstrip(',').encode('utf-8')
			#l = l.lstrip('”').lstrip('。').lstrip('.').lstrip('，').lstrip(',')
			#line[3] = l
			if len(l)>400 or len(l)<5:
                                continue
			for s in strs:
				ss = s.split('\t')
				s = ss[3]
				#print s
				#print l
				#distance = Levenshtein.distance(s,l)
				#print 'distance : '+str(distance) 
				ratio = Levenshtein.ratio(s,l)
				#print 'ratio : '+str(ratio) 
				#if distance<105 and ratio>0.6:
				if ratio>0.6:
					check=False
					break
			if check:
				strs_info.append(lines_info[id])
				strs.append('\t'.join(line))
		return (strs,strs_info)
	
	def _train_data(self,iden,res=None,res_info=None):
		if res==None:
			import cPickle as pickle
			strs = 'classifier/train_res_'+iden+'.txt'
			f=open(strs)
			strs = 'classifier/train_info_'+iden+'.txt'
			f2=open(strs)
			res=pickle.load(f)
			f.close()
			res_info=pickle.load(f2)
			f2.close()
		else:
			(res,res_info)=self._fanhua_extract(iden)
		self.c = Classifier.Classifier(test=False,type='GradientBoostingClassifier',vec='featurehash',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(test=False,type='AdaBoostClassifier',vec='featurehash',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(test=False,type='gaussiannb',vec='union',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(test=False,vec='dictvec',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(type='svc',test=False,vec='featurehash',genre='n_dict',identify=iden)
		self.c.test_train_indri(res,res_info)

	def _proc_upload(self,win,line):
		line = line.strip('\r\n').strip('\n').split('\t')
		line[0] = line[0].strip() 
		strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","'
		for x in self.rels[line[1]]:
			strs += x.encode('utf-8')+' '
		strs=strs.strip()+'"], 500, 40, 10]}\'`'
		print strs
		(llll,lines_info) = self._process_json(strs,line)
		if llll is None:
			print 'indri None '+strs
			return 
		list = self.c.test_test_indri(llll,lines_info)
		if len(list)==0:
			print 'indri + test None '+strs
			return
		ans=line[0]+'\t'+line[1]+'\t'
		count=0
		for l in list:
			if count >=4:
				break
			tline = l.encode('utf-8').split('\t')
                        #win 可修改 0.3 可修改
			if float(tline[3])/(int(tline[4]))<=0.3 or float(tline[3])<win :
				print 'high score result(delete orilen '+tline[4]+' ) : '+l.encode('utf-8')
				continue
			strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+tline[0]+'","'
			for x in self.rels[line[1]]:
				strs += x.encode('utf-8')+' '
			strs=strs.strip()+'","'+tline[2]+'"], 500, 40, 10]}\'`'
			(llll,lines_info) = self._process_json(strs,tline)
			if llll is None:
				print 'high score result( small orilen '+tline[4]+' ) : '+l.encode('utf-8')
				ans+=tline[2]+' '+tline[3]+' '
				count+=1
				continue
			(score,lens) = self.c.test_verify_indri(llll,lines_info)
			if score<0.58 or lens<10 :
				print 'high score result(delete score '+str(score)+' length '+str(lens)+' orilen '+tline[4]+' ) : '+l.encode('utf-8')
				continue
			else:
				print 'high score result( score '+str(score)+' length '+str(lens)+' orilen '+tline[4]+' ) : '+l.encode('utf-8')
				ans+=tline[2]+' '+tline[3]+' '
				count+=1
		return ans.strip()+'\n'

	def _proc_call_shell(self,iden):
		if self.test is False:
			self.c = Classifier.Classifier(type='GradientBoostingClassifier',vec='featurehash',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(type='AdaBoostClassifier',vec='featurehash',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(vec='dictvec',genre='n_dict',identify=iden)
		#self.c = Classifier.Classifier(type='svc',vec='featurehash',genre='n_dict',identify=iden)
		all=0
		current=0
		for line in sys.stdin:
			line = line.strip('\r\n').strip('\n').split('\t')
			try:
				line[0] = line[0].strip() 
				strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","'
				for x in self.rels[line[1]]:
					strs += x.encode('utf-8')+' '
				strs=strs.strip()+'"], 500, 40, 10]}\'`'
				(llll,lines_info) = self._process_json(strs,line)
				if llll is None:
					print 'indri None '+strs
					continue
				list = self.c.test_test_indri(llll,lines_info)
				if len(list)==0:
					print 'indri + test None '+strs
					continue
				ans=line[0]+'\t'+line[1]+'\t'
				count=0
				for l in list:
					if count >=4:
						break
					tline = l.encode('utf-8').split('\t')
					#5 可修改 0.3 可修改
					if float(tline[3])/(int(tline[4]))<=0.3 or float(tline[3])<5 :
						print 'high score result(delete orilen '+tline[4]+' ) : '+l.encode('utf-8')
						continue
					strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+tline[0]+'","'
					for x in self.rels[line[1]]:
						strs += x.encode('utf-8')+' '
					strs=strs.strip()+'","'+tline[2]+'"], 500, 40, 10]}\'`'
					(llll,lines_info) = self._process_json(strs,tline)
					if llll is None:
						print 'high score result( small orilen '+tline[4]+' ) : '+l.encode('utf-8')
						ans+=tline[2]+' '+tline[3]+' '
						count+=1
						continue
					(score,lens) = self.c.test_verify_indri(llll,lines_info)
					if score<0.58 or lens<10 :
						print 'high score result(delete score '+str(score)+' length '+str(lens)+' orilen '+tline[4]+' ) : '+l.encode('utf-8')
						continue
					else:
						print 'high score result( score '+str(score)+' length '+str(lens)+' orilen '+tline[4]+' ) : '+l.encode('utf-8')
						ans+=tline[2]+' '+tline[3]+' '
						count+=1
			except Exception,e:
				traceback.print_exc() 
				continue

	def _fanhua_extract(self,iden):
		res =[]
		res_info = []
		for ll in sys.stdin:
			line = ll.strip('\r\n').strip('\n').split('\t')
			try:
				line[0] = line[0].strip()
				strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","'
				for x in self.rels[line[1]]:
					strs += x.encode('utf-8')+' '
				strs=strs.strip()+'"], 500, 40, 10]}\'`'
				print strs
				#print 'Process indri start'
				strs=commands.getoutput(strs).split('\n')
				js = json.loads(strs[3].replace('\r\n', '').replace('\n',''), strict=False)
				lists = js['result']['_ret']
				#htmls = []
				lines =[]
				lines_info=[]
				cc=0
				for l in lists:
					#h = self.q.sub("",l['docno'])
					#htmls.append(self.q.sub("",l['docno']).encode('utf-8'))
					ls = l['passage'].encode('utf-8')
					if ls.find(line[2]) ==-1:
						if cc>200:
							continue
						cc+=1
						lines.append(line[0]+'\temma\t'+line[2]+'\t'+ls)
						lines_info.append(self._process(l['pass_analyze']))
					else:
						lines.append(line[0]+'\t'+line[1]+'\t'+line[2]+'\t'+ls)
						lines_info.append(self._process(l['pass_analyze']))
				if len(lines)<1:
					continue
				strs = 'echo `curl -XPOST nmg01-kgb-odin3.nmg01:8051/1 -d \'{"method":"search","params" : [["'+line[0]+'","'
				for x in self.rels[line[1]]:
					strs += x.encode('utf-8')+' '
				strs=strs.strip()+'","'+line[2]+'"], 500, 40, 10]}\'`'
				print strs
				strs=commands.getoutput(strs).split('\n')
				js = json.loads(strs[3].replace('\r\n', '').replace('\n',''), strict=False)
				lists = js['result']['_ret']
				for l in lists:
					lines_info.append(self._process(l['pass_analyze']))
					l = l['passage'].encode('utf-8')
					lines.append(line[0]+'\t'+line[1]+'\t'+line[2]+'\t'+l)
				if len(lines)<1:
					continue
				(lines,lines_info) = self._semi_Levenshtein(lines,lines_info)
				for l in xrange(len(lines)):
					res.append(lines[l])
					res_info.append(lines_info[l])
					print lines[l]
				#continue
				#if len(lines)<1:
				#	continue
			except IndexError:
				traceback.print_exc()
				continue
			except Exception,e:
                                traceback.print_exc()
				continue
		import cPickle as pickle
		strs = 'classifier/train_res_'+iden+'.txt'
		print strs
		f=open(strs,'wb')
		strs = 'classifier/train_info_'+iden+'.txt'
		print strs
		f2=open(strs,'wb')
		pickle.dump(res,f)
		f.close()
		pickle.dump(res_info,f2)
		f2.close()
		return (res,res_info)
		
	def _process_json(self,strs,line):
		strs=commands.getoutput(strs).split('\n')
		try:
			js = json.loads(strs[3].replace('\r\n', '').replace('\n',''), strict=False)
		except:
			#print 'error'
			#traceback.print_exc()
			#print strs[3].replace('\r\n', '').replace('\n','').decode('utf-8', 'ignore').encode('utf-8', 'ignore')
			#js = json.loads( unicode(strs[3],'ISO-8859-1'), strict=False )
			js = json.loads(strs[3].replace('\r\n', '').replace('\n','').decode('utf-8', 'ignore').encode('utf-8', 'ignore') ,strict=False )
		lists = js['result']['_ret']
		lines_info = []
		lines = []
		htmls = []
		for l in lists:
			h = self.q.sub("",l['docno'])
			htmls.append(self.q.sub("",l['docno']).encode('utf-8'))
			lines_info.append(self._process(l['pass_analyze']))
			lines.append(l['passage'].encode('utf-8'))
		if len(lines)<1:
			#print 'too small info from indri '+line[0]+'\t'+line[1]+'\t'+line[2]
			return (None,None)
		(lines,lines_info,htmls) = self._semi_without(lines,lines_info,htmls)
		if len(lines)<1:
			#print 'too small info from indri '+line[0]+'\t'+line[1]+'\t'+line[2]
			return (None,None)
		llll=[]
		for idd in xrange(len(lines)):
			l = lines[idd]
			llll.append(line[0]+'\t'+line[1]+'\t'+line[2]+'\t'+l+'\t'+htmls[idd])
		return (llll,lines_info)

	def _process(self,lists):
		seg = []
		lines = []
		pos = []
		dep = []
		for i in xrange(len(lists)):
			l = lists[i]
			if l['word'].strip() == None:
				pass	
			else:
				seg.append(l['word'])
			if l['ner'].strip() == None:
				lines.append("_")
			elif l['ner']=='PER':
				lines.append('PERSON')
			else:
				lines.append(l['ner'])
			if l['postag'].strip() == None:
				pos.append("_")
			else:
				pos.append(l['postag'])
			if l['deprel'].strip() == None or l['head']== None:
                                dep.append('None_None')
			else:
				dep.append(l['deprel']+'_'+str(l['head']))
				#dep.append(l['deprel'])
		return ('\t'.join(seg),'\t'.join(pos),'\t'.join(lines),'\t'.join(dep))

if __name__ == '__main__':
	p=Process()
	if len(sys.argv)==3:
		test = sys.argv[1]
		identify = sys.argv[2]
	elif len(sys.argv)==2:
		test = sys.argv[1]
	else:
		test = 'test'
		identify = 'muqin'
	import time
	start = time.clock()
	start2 = time.time()
	#p._p_fanhua()
	if test == 'test':
		print test
		p._proc_call_shell(identify)
	elif test == 'train':
		print test
		#p._fanhua_extract(identify)
		#p._train_data(identify,res='emma')
		#p._train_data(identify)
		p._train_data('muqin')
		p._train_data('fuqin')
		p._train_data('qizi')
		p._train_data('zhangfu')
		p._train_data('nver')
		p._train_data('erzi')
		p._train_data('nanyou')
		p._train_data('nvyou')
		#TODO 加入新的关系时，训练要加入p._train_data('xinguanxi')
		
	end = time.clock()
	end2 = time.time()
	print end-start
	print end2-start2
	#p._proc_call_shell_high_pv()
