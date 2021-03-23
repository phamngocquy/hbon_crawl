import requests

url = "https://hocbaionha.com/mod/quiz/startattempt.php"

payload='cmid=25&sesskey=B9IpRYL9GJ'
headers = {
    'cookie': 'MoodleSession=fl9ldqjbuo8iglas52igvmltcg;',
    'Content-Type': 'application/x-www-form-urlencoded'
}

res = requests.session()
response = res.request("POST", url, headers=headers, data=payload)
print(response.request.body)
print(response.request.headers)
print(response.request.url)
with open('page.html', 'w') as f:
    f.write(response.text)