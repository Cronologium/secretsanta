import random
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


ENCRYPTED_PEOPLE_FILE = 'encrypted_people.txt'
PEOPLE_FILE = 'people.txt'
KEY_SIZE = 2048

def list_people(people_file):
    people = []
    with open(people_file, 'r') as f:
        people = f.readlines()

    return [person[:-1] if person[-1] == '\n' else person for person in people]


def get_person(certificate_files):
    for certificate_file in certificate_files:
        my_key = None
        with open(certificate_file, "rb") as key_file:
            my_key = serialization.load_pem_private_key(
                key_file.read(),
                password = None,
                backend = default_backend()
            )

        encrypted_people_bytes = open(ENCRYPTED_PEOPLE_FILE, 'rb').read()
        encrypted_people = [encrypted_people_bytes[i:i+KEY_SIZE // 8] for i in range(0, len(encrypted_people_bytes), KEY_SIZE // 8)]

        people = list_people(PEOPLE_FILE)

        found = False
        for encrypted_person in encrypted_people:
            try:
                plaintext = my_key.decrypt(
                    encrypted_person,
                    padding.OAEP(
                        mgf = padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm = hashes.SHA256(),
                        label = None
                    )
                )

                for person in people:
                    if person == plaintext:
                        print('{0}, your person is {1}'.format(certificate_file.split('_')[0], person))
                        found=True
                        break
            except ValueError:
                continue
        if found is False:
            print('{0}, you got nobody :('.format(certificate_file.split('_')[0]))

def cmp_pb_keys(key1, key2):
    return key1.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo) == \
        key2.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

def determine_secret_santas():
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

    with open(ENCRYPTED_PEOPLE_FILE, 'wb') as f:
        f.write(b''.join(crypto_text))

    for x in range(len(private_keys)):
        pem = private_keys[x].private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )

        with open('{0}_ticket.pem'.format(people[x]), 'wb') as f:
            f.write(pem)

if __name__ == '__main__':
    if sys.argv[1] == 'rand':
        determine_secret_santas()
    elif sys.argv[1] == 'get':
        get_person(sys.argv[2:])
    elif sys.argv[1] == 'test':
        determine_secret_santas()
        get_person(['test{0}_ticket.pem'.format(x) for x in range(1, 7)])