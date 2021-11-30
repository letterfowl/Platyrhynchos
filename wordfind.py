from json import dump

from tqdm import tqdm
from bs4 import BeautifulSoup as Soup
from requests import get as webget

LETTERS = 'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż'

words = {}
for letter in tqdm(LETTERS):
    req = webget("https://polski-slownik.pl/hasla-do-krzyzowek.php", params= {'pokaz':'wszystkie', 'na_litere':letter})
    soup = Soup(req.text, features='lxml')
    tags = soup.find('div', class_='card-wrapper').find_all('a')
    for i in tags:
        words[i['title'].removeprefix('Hasła krzyżówkowe: ')] = i.text.lower().replace(" ", "_")
        
with open('words.json', 'w', encoding='utf8') as f:
    dump(words, f)
    
print("Liczba opisów:", len(words))
print("Liczba haseł:", len(set(words.values())))