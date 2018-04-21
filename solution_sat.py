import solution
from satispy import Variable, Cnf
from satispy.solver import Minisat

N = solution.N
N_B = solution.N_B

# Get indexes of zeros in SUB in CNF.
def get_zeroes_cnf(v1, v2, v3):
    cnf = Cnf()
    cnf &= (-v1 & -v2 & -v3) | (-v1 & v2 & v3) | (v1 & -v2 & v3) | (v1 & v2 & v3)
    return cnf

# Get indexes of ones in SUB in CNF.
def get_ones_cnf(v1, v2, v3):
    cnf = Cnf()
    cnf &= (-v1 & -v2 & v3) | (-v1 & v2 & -v3) | (v1 & -v2 & -v3) | (v1 & v2 & -v3)
    return cnf

# Get the CNF containing all variables (bits).
def get_keystream_cnf(y, x_bits, change):
    cnf = Cnf()
    for i in range(N-1, -1, -1):
        if ((y >> i) & 1) == 1:
            cnf &= get_ones_cnf(x_bits[i+2], x_bits[i+1], x_bits[i])
        else:
            cnf &= get_zeroes_cnf(x_bits[i+2], x_bits[i+1], x_bits[i])
    cnf &= change
    return cnf

def reverse_step(y):
    x_bits = []
    for i in range(N+2):
        x_bits.append(Variable(str(i)))
    solver = Minisat()
    cnf = Cnf()
    changes = [x_bits[N+1] &  x_bits[N]
             , x_bits[N+1] & -x_bits[N]
             ,-x_bits[N+1] &  x_bits[N]
             ,-x_bits[N+1] & -x_bits[N]]
    for change in changes:
        cnf = get_keystream_cnf(y, x_bits, change)
        sol = solver.solve(cnf)
        x = 0
        for i in range(N+1):
            x |= sol[x_bits[i]] << i
        x = (x >> 1) & (2**N - 1)
        if solution.step(x) == y:
            # The reversion succeeded.
            return x

ks = solution.get_keystream()
# Perform reversion of the keystream initialization.
for i in range(N // 2):
    ks = reverse_step(ks)
# Print the key.
print(ks.to_bytes(N_B, 'little').decode(), end='')
