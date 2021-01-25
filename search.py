import PyPDF2
from tqdm import tqdm
from pickle import dump,load
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

pdfFileName = 'real_analysis_ross.pdf'
loadCacheFromDisk = True
keywords = ['cauchy','series']

# constants
INDENT = ' '*4

pdfReader = PyPDF2.PdfFileReader(pdfFileName)

# extract metadata
pdfInfo = pdfReader.getDocumentInfo()
numPages = pdfReader.getNumPages()

print()
print('loaded pdf:',flush=True)
print(f'{INDENT}title: {pdfInfo.title}',flush=True)
print(f'{INDENT}author: {pdfInfo.author}',flush=True)
print(f'{INDENT}creator: {pdfInfo.creator}',flush=True)
print(f'{INDENT}producer: {pdfInfo.producer}',flush=True)
print()

# cache all page text in memory
cachedTextFileName = pdfFileName.split('.')[0] + '.pickle'
pdfText = None
pageLens = None

if loadCacheFromDisk:
    print('loading previously cached page text from disk...')
    try:
        with open(cachedTextFileName,'rb') as cachedTextFile:
            pdfText,pageLens = load(cachedTextFile)
        print('finished.\n',flush=True)
    except:
        print('failed. (does not exist or incorrect format)\n',flush=True)
        pdfText = None
        pageLens = None

if pdfText is None or pageLens is None:
    print(f'caching page text in memory...',flush=True)

    pdfText = [None for _ in range(numPages)]
    pageLens = [None for _ in range(numPages)]
    for pageNum in tqdm(range(numPages),ncols=90):
        pageText = pdfReader.getPage(pageNum).extractText().lower()
        pdfText[pageNum] = pageText
        pageLens[pageNum] = len(pageText)

    print(f'\nfinished.\n',flush=True)

    print(f'saving to disk for future use...',flush=True)
    with open(cachedTextFileName,'wb') as cachedTextFile:
        dump((pdfText,pageLens),cachedTextFile)
    print(f'finished.\n',flush=True)

print(f'starting search for occurances of {str(keywords)}...')
keywordOccurances = []
pageLenSum = 0
for pageNum,pageText in tqdm(enumerate(pdfText)):
    pageOccurances = []
    for keyword in keywords:
        pageOccurances.extend(
            map(
                lambda pageI: [pageLenSum + pageI,keyword,pageNum],
                [m.start() for m in re.finditer(keyword,pageText)]
            )
        )
    keywordOccurances.extend(sorted(pageOccurances,key=lambda o: o[0]))
    pageLenSum += pageLens[pageNum]
print('finished.\n')

print(f'starting search for clusters of {str(keywords)}...')
minDist = float('+inf')
lastOccurance = [None,None]
for wordIndex,keyword,pageNum in keywordOccurances:
    