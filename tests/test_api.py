import requests

url = "http://localhost:8030/chat"
headers = {"Content-Type": "application/json"}

payload = {
    "input": {
        "question": "Що таке роумiнг?",
        "language": "Ukrainian",
        "session_id": "optional-session-id"
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

response1 = requests.post(url, json={
    "input": {
        "question": "What is 'My Kyivstar'?",
        "language": "English"
    }
})
print(response1.json())
session_id = response.json()["session_id"]

response2 = requests.post(url, json={
    "input": {
        "question": "Про що я тільки що запитав?",
        "language": "English",
        "session_id": session_id
    }
})
print(response2.json())