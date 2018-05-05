
from bittrex.bittrex import Bittrex, API_V1_1

bittrex = Bittrex("c7f58b74b3d74895af1a428e805dc7c2", "eb746744efeb4a5190161c6ad60b1338", api_version=API_V1_1)

print (bittrex.get_balances())
