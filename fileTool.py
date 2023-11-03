#!/usr/bin/env python3

from cryptography.fernet import Fernet
import sys
import os
import subprocess
import random
import re


# Function to encrypt a file's contents and output them into a new file
# Will also delete the original file 
def encrypt(inputFile, email):
    hashkey = ''
    filePath = os.path.join('.', 'filekey.key')
    if os.path.exists(filePath):
        with open('filekey.key', 'rb') as filekey:
            hashkey = filekey.read()
    else:
        hashkey = Fernet.generate_key()
        with open('filekey.key', 'wb') as filekey:
            filekey.write(hashkey)

    

    with open(inputFile, 'rb') as fileIn:
        fileContent = fileIn.read()

    encryption = Fernet(hashkey)
    encryptedContent = encryption.encrypt(fileContent)

    with open(inputFile, 'wb') as replaceContent:
        replaceContent.write(encryptedContent)

    MFAnumber = random.randint(100000, 999999)
    newData = f"{inputFile}|{MFAnumber}"
    with open('dataVerification.txt', "a") as file:
        file.write(newData + "\n")
    
    subject = f"Two Factor Authentication for encrypted file '{inputFile}'"
    message_body = f"The authentication key is: {MFAnumber}"

    mutt_command = f'mutt -s "{subject}" {email}'
    proc = subprocess.Popen(mutt_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


    email_content = f'{message_body}\n'
    proc.communicate(input=email_content)

    proc.stdin.close()
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()
    

def decrypt(fileName):
    storeKey = ''
    with open('filekey.key', 'rb') as filekey:
        storeKey = filekey.read()

    with open(fileName, 'rb') as file:
        fileContent = file.read()

    decryption = Fernet(storeKey)
    decryptedContent = decryption.decrypt(fileContent)

    with open(fileName, 'wb') as fileOut:
        fileOut.write(decryptedContent)

    for line in open('dataVerification.txt', 'r'):
        currLine = line.split("|")
        if (re.match(currLine[0], fileName)):
            del line
            break


def verification(fileName, code):
    getCode = 0
    for line in open('dataVerification.txt', 'r'):
        currLine = line.strip()
        currLine = currLine.split("|")
        if (re.match(currLine[0], fileName)):
            getCode = currLine[1]
            if (getCode == code):
                return True
            else:
                return False
    return False



encryptOrDecrypt = input("Would you like to encrypt or decrypt a file?\n")

if (encryptOrDecrypt == 'encrypt'):
    fileName = input("What is the name of the file you would like to encrypt?\n")
    email = input("And what is a valid email that can be used for 2-factor authentication?\n")

    encrypt(fileName, email)
elif (encryptOrDecrypt == 'decrypt'):
    fileName = input("What is the name of the file you would like to decrypt?\n")
    MFAcheck = input("Please provide the 6-digit pin that was sent to your email upon encryption.\n")

    if (verification(fileName, MFAcheck)):
        decrypt(fileName)
    else:
        print("Error")        