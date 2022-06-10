# import secrets

# FLAG = b'grey{...}'
#
# assert len(FLAG) == 40
FLAG = bytes.fromhex('982e47b0840b47a59c334facab3376a19a1b50ac861f43bdbc2e5bb98b3375a68d3046e8de7d03b4')
key = b'grey'

def encrypt(m):
    return bytes([x ^ y for x, y in zip(m,key)])

c = b''
for i in range(0, len(FLAG), 4):
    c += encrypt(bytes(FLAG[i : i + 4]))

print(c[:4].hex())

# 982e47b0840b47a59c334facab3376a19a1b50ac861f43bdbc2e5bb98b3375a68d3046e8de7d03b4