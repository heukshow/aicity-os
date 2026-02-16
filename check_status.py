
import urllib.request
import urllib.error

urls = [
    "http://localhost:8000/crew.html",
    "http://localhost:8000/projects/Cauchemar/crew.html",
    "http://localhost:8000/projects/Cauchemar/data/crew.json"
]

for url in urls:
    try:
        code = urllib.request.urlopen(url).getcode()
        print(f"{url}: {code}")
    except urllib.error.HTTPError as e:
        print(f"{url}: {e.code}")
    except Exception as e:
        print(f"{url}: Error {e}")
