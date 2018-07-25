package lib

import (
	"encoding/base64"
	"encoding/hex"
	"fmt"
	crypto "github.com/tendermint/tendermint/crypto"
	"github.com/tendermint/tendermint/p2p"
)

type PubkeyType crypto.PubKey
type SigType crypto.Signature

var prvkey *p2p.NodeKey
var err error

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
