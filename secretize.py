import random
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

PEOPLE_FILE = 'people.txt'
KEY_SIZE = 2048

def encode_int(x):
    return '{0}{1}{2}{3}'.format(x % 10, x // 10 % 10, x // 100 % 10, x // 1000 % 10)

def decode_int(b):
    return int(b[0]) + int(b[1]) * 10 + int(b[2]) * 100 + int(b[3]) * 1000

def list_people(people_file):
    people = []
    with open(people_file, 'r') as f:
        people = f.readlines()

    return [person[:-1] if person[-1] == '\n' else person for person in people]

def open_ticket(ticket):
    my_key = None
    encrypted_people = []
    with open(ticket, 'rb') as f:
        cert_length = decode_int(f.read(4))
        my_key = serialization.load_pem_private_key(
            f.read(cert_length),
            password=None,
            backend=default_backend()
        )
        encrypted_people_bytes = f.read()
        encrypted_people = [encrypted_people_bytes[i:i + KEY_SIZE // 8] for i in
                            range(0, len(encrypted_people_bytes), KEY_SIZE // 8)]

    found = False
    for encrypted_person in encrypted_people:
        try:
            plaintext = my_key.decrypt(
                encrypted_person,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            print('{0}, your person is {1}'.format(ticket.split('.')[0], plaintext))
            return
        except ValueError:
            continue

    if found is False:
        print('{0}, you got nobody :(\n(Could not find a valid person)'.format(ticket.split('.')[0]))

def cmp_pb_keys(key1, key2):
    return key1.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo) == \
        key2.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

def write_ticket(person, cert, people):
    with open('{0}.ticket'.format(person), 'wb') as f:
        f.write(encode_int(len(cert)) + cert + people)

def generate_tickets(people=None):
    if people is None:
        people = list_people(PEOPLE_FILE)

    private_keys = []
    crypto_text = []

    for line in people:
        if line.endswith('\n'):
            line = line[:-1]

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=KEY_SIZE,
            backend=default_backend()
        )

        crypto_text.append(private_key.public_key().encrypt(
            line,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ))

        private_keys.append(private_key)

    init_order = [prv_key for prv_key in private_keys]

    ok = False
    while ok is False:
        random.shuffle(private_keys)

        ok = True
        for x in range(len(init_order)):
            if cmp_pb_keys(init_order[x], private_keys[x]):
                #print('[DEBUG] Not ok, {0} gets himself'.format(people[x]))
                ok = False

    for x in range(len(private_keys)):
        pem = private_keys[x].private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )
        write_ticket(people[x], pem, b''.join(crypto_text))

if __name__ == '__main__':
    if sys.argv[1] == 'gen':
        if len(sys.argv) > 3:
            generate_tickets(sys.argv[2:])
        else:
            generate_tickets()
    elif sys.argv[1] == 'open':
        open_ticket('{0}.ticket'.format(sys.argv[2]))
    elif sys.argv[1] == 'test':
        generate_tickets(['test1', 'test2', 'test3'])
        for x in range(1,4):
            open_ticket('test{0}.ticket'.format(x))