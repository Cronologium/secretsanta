# SecretSanta
An algorithm which solves the hassle of distributing pieces of paper to people for secret santa

# Problem statement

Based on the question listed [here](https://math.stackexchange.com/questions/2896780/secret-santa-algorithm-that-does-not-rely-on-a-trusted-3rd-party),  the aim is to create a method in which users do not use physical paper and do not have access to other people's tickets. (except for the master shuffler at the begining)

# Setup

In order to run the program, you'll need Python3 installed and the [cryptography pip package](https://cryptography.io/en/latest/). In order to install it, run: 

`sudo pip install cryptography`

# How it works

This code serves two purposes: shuffling/generating tickets and reading tickets. Each ticket is a private key (PEM) consisting of 2048 bytes plus the names of the people as encrypted text.

For the shuffling phase, people listed in the _people.txt_ are each encrypted with a different public key using RSA. The public key is then dismissed, but the private key is saved into a file which has the name of one of the participants (but not the name of the person which is currently encrypted). At the end, a .ticket file has generated for each person containing its private key and all the participants' names encrypted.

In order for each participant to determine the person, they will try to decrypt all the peoples' names using the ticket (private key) until one works.

# How to use:

One person is enough to shuffle the tickets, while the rest should be able to read them. So, all the people participating in secret Santa should be able to run this script. 

For the person shuffling the tickets: after shuffling, send the tickets to the respective people. Do not open them or keep them. It ruins the surprise :)

To shuffle tickets:

`python secretize.py gen # you need a file called people.txt`

or

`python secretize.py gen Andrew Betty Christian Dorothy`

To read ticket:

`python secretize.py open <.ticket file>`
