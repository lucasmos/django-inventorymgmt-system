import requests

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer 0aGGY8YTGwJYB9lQhwpJTnzlHFxF'
}

payload = {
    "BusinessShortCode": 174379,
    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwNDI3MTM1ODE3",
    "Timestamp": "20240427135817",
    "TransactionType": "CustomerPayBillOnline",
    "Amount": 1,
    "PartyA": 254729293714,
    "PartyB": 174379,
    "PhoneNumber": 254729293714,
    "CallBackURL": "https://mydomain.com/path",
    "AccountReference": "CompanyXLTD",
    "TransactionDesc": "Payment of X" 
  }

response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers = headers, data = payload)
print(response.text.encode('utf8'))