from __future__ import absolute_import
import os
import subprocess
from user.models import ABCIUser

CryptoBinFile="crypto"
DataBinFile="getdata"
DefaultKeyPath='./'

def Execute(BinFile,CMD):
    execcmd = BinFile + CMD
    o = os.popen(execcmd).read()
    return o
    #p = subprocess.Popen(execcmd, shell=True, stdout=subprocess.PIPE)
    #return p.communicate()

def CryptoExec(CMD):
    return Execute(CryptoBinFile,CMD)

def DataExec(CMD):
    return Execute(DataBinFile,CMD)

def GetPubkey(user,keypath=None):
    if keypath is None:
        keypath = DefaultKeyPath
    cmd = ' -mode pub -key '+ keypath + user + '-prv.json'
    return CryptoExec(cmd)

def GeneratePrvkey(user,keypath=None):
    if keypath is None:
        keypath = DefaultKeyPath
    cmd = " -mode key -key " + keypath + user + '-prv.json'
    return CryptoExec(cmd)

def adduser(user):
    path = GeneratePrvkey(user)
    pub = GetPubkey(user)

    u1 = ABCIUser(username=user, prvkey_file=path, pubkey=pub)
    u1.save()

if __name__ == '__main__':
    out = Execute(CryptoBinFile," -mode pub")
    print("default pub:%s"%out)

    sellerpub = GetPubkey('seller')
    print("seller's pub:%s"%sellerpub)