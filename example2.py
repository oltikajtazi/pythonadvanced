from bs4 import BeautifulSoup

html_content =("<html><head><title>hello there</title></head><body><h1>Welcome to beautiful soup</h1><p class=intro>beautiful soup easy!</p><div id=content><p>here are some link</p><a>link 1</a><a>link 2</a><a>link 3 </a></div></body></html>")

soup = BeautifulSoup(html_content,'html.parser')




print("Title of the page:",soup.title.text)
intro_text = soup.find('p', class_='intro')
print(intro_text)
aasdfast = soup.find('div',id="content")

links = div_content.find_all('a')

print(links)