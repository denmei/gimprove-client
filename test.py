import requests
import json

response = requests.get("https://gimprove-test.herokuapp.com/tracker/userprofile_detail_rest/", headers={'Authorization': 'Token d6732690ca3cf7c2b04716f344e983166491d762'})
print(response.status_code)
print((response.content.decode("utf-8")))
