from bs4 import BeautifulSoup

html_content =("<html><body><p>hello, klasa 7:30b</p></body></html>")

soup = BeautifulSoup(html_content,'html.parser')


paragrafi = soup.find('p').text

print(paragrafi)