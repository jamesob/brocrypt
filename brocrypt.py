#!/usr/bin/env python
"""
This script encrypts a given file with a single-use 128-bit key using AES
(Fernet).  It then echoes instructions to be distributed to others with the
idea that they will be able to decrypt the message if they have access to two
(relateively) secure storage locations.

- The key and decryption instructions are stored in one service (email,
  Dropbox, 1password, etc.)

- The encrypted message itself is stored in another service, indexed somehow
  by the hash of the Fernet key.

This requires that an adversary gain access to 2 independent sources in
order to decrypt the plaintext.

"""
import argparse
import sys
import hashlib
from textwrap import dedent

from cryptography.fernet import Fernet


NAME = "brocrypt"
INSTALL_URL = (
    "https://raw.githubusercontent.com/jamesob/brocrypt/master/install")
IS_3 = sys.version_info[0] >= 3


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()

    def add_filename(p):
        p.add_argument(
            'filename', nargs='?', default='-', type=str,
            help=(
                "The name of the file to be operated on. "
                "If not specified, read from stdin."
            ),
        )

    enc_parser = subparsers.add_parser('enc')
    enc_parser.set_defaults(func=enc)
    add_filename(enc_parser)

    dec_parser = subparsers.add_parser('dec')
    dec_parser.set_defaults(func=dec)
    dec_parser.add_argument(
        'key', type=str, help='The base64 key to use for decryption.')
    add_filename(dec_parser)

    return parser


def enc(args):
    to_enc = get_file_contents(args.filename)
    key = Fernet.generate_key()
    f = Fernet(key)

    if IS_3:
        to_enc = to_enc.encode()

    token = f.encrypt(to_enc)
    keyhash = hashlib.sha1(key).hexdigest()

    if IS_3:
        token = token.decode()
        key = key.decode()

    print(dedent(
        """
        Make this encrypted message accessible in some hosted service (email, Dropbox,
        1password, etc.) identified by the key id "{keyhash}" (e.g. use this as an email
        subject line). If you're sharing this with someone else, email it or
        send it to them.

        -----------------------------------------------------------------------
        {token}
        -----------------------------------------------------------------------

        Then, share these decryption instructions in another hosted service:

        -----------------------------------------------------------------------
        You've been given an encrypted message.

        To unencrypt the message, place the message payload identified by
        "{keyhash}" (check your email) into a file called "infile".

        Then run

        curl {programurl} | bash
        {programname} dec {key} infile

        !!! Remember to delete any files containing this information.
        -----------------------------------------------------------------------
        """.format(
            keyhash=keyhash,
            token=token,
            key=key,
            programname=NAME,
            programurl=INSTALL_URL,
        )))


def dec(args):
    to_dec = get_file_contents(args.filename)
    to_dec = to_dec.encode() if IS_3 else to_dec
    key = args.key.encode() if IS_3 else args.key
    f = Fernet(key)
    msg = f.decrypt(to_dec)
    msg = msg.decode() if IS_3 else msg
    print(msg)


def get_file_contents(filename=None):
    if filename and filename != '-':
        with open(filename, 'r') as f:
            return f.read()

    return sys.stdin.read()


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
