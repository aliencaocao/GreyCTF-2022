from pwn import *
from collections import deque

io = remote('challs.nusgreyhats.org', 15521)


def eval_expr(tokens):
    token = tokens.popleft()
    if token == 'add':
        return eval_expr(tokens) + eval_expr(tokens)
    elif token == 'sub':
        return eval_expr(tokens) - eval_expr(tokens)
    elif token == 'mul':
        return eval_expr(tokens) * eval_expr(tokens)
    elif token == 'inc':
        return eval_expr(tokens) + 1
    elif token == 'neg':
        return -eval_expr(tokens)
    else:
        return int(token)


io.recvuntil(b'Send START when you are ready!')
io.sendline(b'START')
for i in range(100):
    io.recvline()
    expr = io.recvline().decode()
    #print(expr)
    ans = eval_expr(deque(expr.split()))
    #print(ans)
    io.sendline(str(ans).encode())
    io.recvuntil(b'You got it right!')
io.interactive()
