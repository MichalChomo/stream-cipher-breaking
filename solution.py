import sys

SUB = [0, 1, 1, 0, 1, 0, 1, 0]
N_B = 32
N = 8 * N_B

# Perform a step on N bits of a keystream of the stream cipher.
def step(x):
    x = (x & 1) << N+1 | x << 1 | x >> N-1
    y = 0
    for i in range(N):
        y |= SUB[(x >> i) & 7] << i
    return y

# Get the triplet containing the two given MSB.
def find_triplet_by_two_msb(msb, triplets):
    return [t for t in triplets if msb == (t >> 1)][0]

# Get the reversed value of the given keystream with two given MSB prepended.
def try_reverse(msb, y):
    # 0's in y can map to these 3-bit combinations.
    zero_triplets = [0, 3, 5, 7]
    # 1's in y can map to these 3-bit combinations.
    one_triplets = [1, 2, 4, 6]
    x = 0
    for i in range(N-1, -1, -1):
        if ((y >> i) & 1) == 1:
            x |= find_triplet_by_two_msb(msb, one_triplets) << i
        else:
            x |= find_triplet_by_two_msb(msb, zero_triplets) << i
        msb = (x >> i) & 3
    return x

# Get the reversed value of the given keystream.
def reverse_step(y):
    # There are 4 possible combinations for the two MSB of x.
    for msb in range(4):
        x = try_reverse(msb, y)
        x = (x >> 1) & (2**N - 1)
        if step(x) == y:
            # The reversion succeeded.
            return x

# XOR two byte arrays.
def bytes_xor(a, b) :
    return bytes(x ^ y for x, y in zip(a, b))

# Get first N_B bytes of the keystream as int.
def get_keystream():
    # Read the ciphertext and plaintext files, only N_B bytes are required.
    with open('in/bis.txt.enc', 'rb') as enc_file:
        enc = enc_file.read(N_B)
    with open('in/bis.txt', 'rb') as plain_file:
        plain = plain_file.read(N_B)
    # Get the keystream by XOR-ing the ciphertext with plaintext.
    keystream = bytes_xor(enc, plain)
    # Return the integer representation of the keystream.
    return int.from_bytes(keystream[:N_B], 'little')

if __name__ == "__main__":
    ks = get_keystream()
    # Perform reversion of the keystream initialization.
    for i in range(N // 2):
        ks = reverse_step(ks)
    # Print the key.
    print(ks.to_bytes(29, 'little').decode(), end='')
