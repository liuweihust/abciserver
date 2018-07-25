package lib

import (
	"encoding/base64"
	"encoding/hex"
	"fmt"
	//secp256k1 "github.com/btcsuite/btcd/btcec"
	crypto "github.com/tendermint/tendermint/crypto"
	"github.com/tendermint/tendermint/p2p"
)

type PubkeyType crypto.PubKey

//type PrvkeyType crypto.PubKey
type SigType crypto.Signature

const SecretLen = 32

var prvkey *p2p.NodeKey
var err error
var receiver crypto.PubKey

func Generate(filePath string) error {
	prvkey, err = p2p.LoadOrGenNodeKey(filePath)
	if err != nil {
		return err
	}
	return nil
}

func Kid() p2p.ID {
	return prvkey.ID()
}

func Getpubkey() []byte {
	return prvkey.PubKey().Bytes()
}

func Sign(msg []byte) string {
	signature, err := prvkey.PrivKey.Sign(msg)
	if err != nil {
		panic(err)
	}
	encodeString := base64.StdEncoding.EncodeToString(signature.Bytes())
	return encodeString
}

//If sig match pubkey and msg, will return true, else return false
func CheckSig(pubkey string, msg string, sig string) bool {
	var err error

	decodeBytes, err := base64.StdEncoding.DecodeString(sig)
	if err != nil {
		fmt.Printf("Fail to base64 decode sig:%s\n", sig)
		return false
	}

	csig, err := crypto.SignatureFromBytes([]byte(decodeBytes))
	if err != nil {
		fmt.Printf("Fail to build signature:%v\n", decodeBytes)
		return false
	}

	decode, err := hex.DecodeString(pubkey)
	if err != nil {
		fmt.Printf("Fail to hex decode pubkey:%v\n", pubkey)
		return false
	}
	cpk, err := crypto.PubKeyFromBytes(decode)
	if err != nil {
		fmt.Printf("Fail to build pubkey:%v\n", decode)
		return false
	}

	return cpk.VerifyBytes([]byte(msg), csig)
}

func NewCipher(plaintext []byte) ([]byte, []byte) {
	secret := crypto.CRandBytes(SecretLen)
	ciphertext := crypto.EncryptSymmetric(plaintext, secret)
	return secret, ciphertext
}

func DeCipher(ciphertext []byte, secret []byte) ([]byte, error) {
	plaintext, err := crypto.DecryptSymmetric(ciphertext, secret)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		return nil, err
	}
	return plaintext, nil
}

func ImportReceiver(pubstr string) error {
	decode, err := hex.DecodeString(pubstr)
	if err != nil {
		return err
	}
	receiver, err = crypto.PubKeyFromBytes(decode)

	return err
}

func SendReceiver(plaintext []byte) ([]byte, error) {
	return PubEncrypt(plaintext, receiver)
}

func PubEncrypt(plaintext []byte, pubkey PubkeyType) ([]byte, error) {
	return nil, nil
}

func PrvDecrypt(ciphertext []byte, prvkey p2p.NodeKey) ([]byte, error) {
	return nil, nil
}
