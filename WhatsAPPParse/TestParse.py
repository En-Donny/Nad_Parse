# import requests
#
# ID_INSTANCE = "1101792531"
# API_TOKEN_INSTANCE = "eb938699e4f247f78be65e6c76c85abe0684ec79300e4fc09b"
#
# url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/lastIncomingMessages/{API_TOKEN_INSTANCE}?minutes=3240"
#
# payload = {}
# headers = {}
#
# response = requests.request("GET", url, headers=headers, data=payload)
#
# print(response.text.encode('utf8'))

str = '79053880270@c.us'
print(str[:-5])

from datetime import datetime
ts = int('1284101485')

print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
