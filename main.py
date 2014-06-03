# coding: windows-1253
import os
import sys
import shutil
import string
import collections
import operator
import re
import numpy
import time

#############################################################################

def splitParagraphIntoSentences(paragraph):
	#regular expressions are easiest (and fastest)
	sentenceEnders = re.compile('[.!?;]')
	sentenceList = sentenceEnders.split(paragraph)
	sentenceList.pop(len(sentenceList)-1)
	return sentenceList


def OpenAndDecode(filename):
	# try to open and decode the file; exit if some IOError occurs
	try:
		f = open(filename, 'r').read()
		data = f.decode('windows-1253','replace')
	except Exception:
		#data = f.decode('windows-1253','replace')
		print "Unexpected error:", sys.exc_info()[0]
		data="d"
		sys.exit(1)
	return data#.encode('utf-8')


def NormalizeWord(word):
	#Strip punctuation
	cha='»'.decode('windows-1253')
	chb='�'.decode('windows-1253')
	chc='«'.decode('windows-1253')
	chd='–'.decode('windows-1253')
	word=word.strip(cha+chb+chc+chd+'!?;:.,\'\'\"\"()[]-')
	# Change to lower case
	word=string.lower(word)
	return word


def GetWordsOfString(string):
	wordlist=string.split()
	for i in range(0,len(wordlist)):
		wordlist[i]=NormalizeWord(wordlist[i])
	return wordlist


def GetFirstWordsOfSentencesplusCompinedWords(string,MM):
	Sentences = splitParagraphIntoSentences(string)
	wordlist = []#Sentences
	for i in range(0,len(Sentences)):
		try:
			if NormalizeWord(Sentences[i].split()[0])!='':
				wordlist.append(NormalizeWord(Sentences[i].split()[0]))
		except Exception:
			log=1
			#print "Unexpected error:", sys.exc_info()[0]
	wordlistComp = []#Sentences	
	for i in range(0,len(Sentences)):
		try:
			plainwords=Sentences[i].split()
			for j in range(0,len(plainwords)-1):
				wordcompined=NormalizeWord(plainwords[j])+'^&*'+NormalizeWord(plainwords[j+1])
				wordlistComp.append(wordcompined)
		except Exception:
			log=1
			#print "Unexpected error:", sys.exc_info()[0]
	return wordlist,wordlistComp


def GetAllWordsplusCompinedWords(string,MM):
	wordlist=GetWordsOfString(string)
	Sentences = splitParagraphIntoSentences(string)
	wordlistComp = []#Sentences	
	for i in range(0,len(Sentences)):
		try:
			plainwords=Sentences[i].split()
			for j in range(0,len(plainwords)-1):
				wordcompined=NormalizeWord(plainwords[j])+'^&*'+NormalizeWord(plainwords[j+1])
				wordlistComp.append(wordcompined)
		except Exception:
			log=1
			#print "Unexpected error:", sys.exc_info()[0]
	return wordlist,wordlistComp


def GetDictionaries(Dataset,MM):
	if MM==0:
		##Init Dictionaries
		dictionaries =[collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()]
		wordsNos = [0,0,0,0,0,0,0]
		for i in range (0,len(Dataset)):
			wordsi=GetWordsOfString(Dataset[i])
			#Each dictionary - Hash table Dictionary
			dictionaries[i].update(wordsi)
			wordsNos[i]=len(wordsi)
			##Alldictionary
			dictionaries[6].update(wordsi)
			wordsNos[6] = wordsNos[6] + wordsNos[i]

		dictionaries2, wordsNos2 ,dictionaries3 = 0,0,0 #Just to return something we use them at mm-1

	else:
		##Init Dictionaries
		dictionaries =[collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()]
		wordsNos = [0,0,0,0,0,0,0]
		dictionaries2 =[collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()]
		wordsNos2 = [0,0,0,0,0,0,0]
		dictionaries3 =[collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()]
		for i in range (0,len(Dataset)):
			wordsi,wordlistComp=GetAllWordsplusCompinedWords(Dataset[i],MM)
			#Each dictionary - Hash table Dictionary
			dictionaries[i].update(wordsi)
			wordsNos[i]=len(wordsi)
			##Alldictionary
			dictionaries[6].update(wordsi)
			wordsNos[6] = wordsNos[6] + wordsNos[i]
			#Each dictionary2 - Hash table Dictionary
			dictionaries2[i].update(wordlistComp)
			wordsNos2[i]=len(wordlistComp)
			##Alldictionary2
			dictionaries2[6].update(wordlistComp)
			wordsNos2[6] = wordsNos2[6] + wordsNos2[i]

		for i in range (0,len(Dataset)):
			wordsi,wordlistComp=GetAllWordsplusCompinedWords(Dataset[i],MM)
			wordsj=[]
			for j in (0,len(wordsi)):
				try:
					wordsj.append(wordsi[j].split('^&*')[0])
				except Exception:
					log=1
			dictionaries3[i].update(wordsj)

	return dictionaries,wordsNos,dictionaries2,wordsNos2,dictionaries3


def test(dictionaries,wordsNos,dictionaries2,wordsNos2,dictionaries3,CatNos,DatasetTEST,MM):
	Prop = [0,0,0,0,0,0]
	if MM==0:
		wordTest=GetWordsOfString(DatasetTEST)
		for i in range (0, len(Prop)):
			for word in wordTest:
				if dictionaries[i][word]!=0:
					Prop[i]=Prop[i]+numpy.log(dictionaries[i][word])-numpy.log(wordsNos[i])
				else:
					Prop[i]=Prop[i]-numpy.log(wordsNos[i])
			Prop[i]=Prop[i]+numpy.log(CatNos[i])-numpy.log(CatNos[6])

	else:
		wordTestFirst,wordTestComp=GetFirstWordsOfSentencesplusCompinedWords(DatasetTEST,MM)
		#FIRST
		for i in range (0, len(Prop)):
			for word in wordTestFirst:
				if dictionaries[i][word]!=0:
					Prop[i]=Prop[i]+numpy.log(dictionaries[i][word])-numpy.log(wordsNos[i])
				else:
					Prop[i]=Prop[i]-numpy.log(wordsNos[i])
		#COMP
			#k=0
			for word in wordTestComp:
				#print k
				#k=k+1

				#eq 10
				#Nos2=100
				Nos2=100+dictionaries3[i][word.split('^&*')[0]]
				#1q 11
				#Nos2=100+dictionaries[i][word.split('^&*')[0]]
				

				if dictionaries2[i][word]!=0:
					Prop[i]=Prop[i]+numpy.log(dictionaries2[i][word]+100)-numpy.log(Nos2)
				else:
					Prop[i]=Prop[i]-numpy.log(Nos2)

			Prop[i]=Prop[i]+numpy.log(CatNos[i])-numpy.log(CatNos[6])
	return Prop

#############################################################################
if __name__ == '__main__':
	##################### init Data
	path="./train/"
	Dataset =[OpenAndDecode(path+"art"+"/"+"art"+".dat"), OpenAndDecode(path+"economy"+"/"+"economy"+".dat"), OpenAndDecode(path+"greece"+"/"+"greece"+".dat"), OpenAndDecode(path+"politics"+"/"+"politics"+".dat"), OpenAndDecode(path+"sport"+"/"+"sport"+".dat"), OpenAndDecode(path+"world"+"/"+"world"+".dat")]
	CatNos=[663,899,782,735,909,664,(663+899+782+735+909+664)]
	##################### TRAIN
	MarkovChainOrder=1
	##
	dictionaries,wordsNos,dictionaries2,wordsNos2,dictionaries3 = GetDictionaries(Dataset,MarkovChainOrder)
	print "Init Completed"
	##################### TEST
	CatNostest=[368,518,470,422,479,396]
	Categories=['art','economy','greece','politics','sport','world']
	for j in range(0,6):
		Accuracy=0
		for i in range(0,CatNostest[j]):
			DatasetTEST = OpenAndDecode("./test/"+Categories[j]+"/"+Categories[j]+str(i))
			Prop = test(dictionaries,wordsNos,dictionaries2,wordsNos2,dictionaries3,CatNos,DatasetTEST,MarkovChainOrder)	
			Prop.index(max(Prop))
			if Prop.index(max(Prop))==j:
				Accuracy=Accuracy+1
		print Categories[j],"Category accuracy:",float(Accuracy*100/CatNostest[j]),"%"                           
