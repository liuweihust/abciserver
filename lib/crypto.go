package lib

import (
	"encoding/base64"
	"fmt"
	crypto "github.com/tendermint/tendermint/crypto"
	"github.com/tendermint/tendermint/p2p"
	//"reflect"
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
	/* base64 encoding, maybe use in future
	fmt.Println(encodeString)
	*/
	/*
		decodeBytes, err := base64.StdEncoding.DecodeString(msg)
		signature, err := prvkey.PrivKey.Sign(decodeBytes)
	*/
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
	if err != nil{
		fmt.Printf("Fail to base64 decode sig:%s\n", sig)
		return false
	}

	csig,err := crypto.SignatureFromBytes([]byte(decodeBytes))
	if err != nil{
		fmt.Printf("Fail to build signature:%v\n", decodeBytes)
		return false
	}
	fmt.Printf("csig:%v\n", csig)

	cpk,err := crypto.PubKeyFromBytes([]byte(pubkey))
	if err != nil{
		fmt.Printf("Fail to build pubkey:%s\n", pubkey)
		return false
	}

	fmt.Printf("cpub:%v,csig:%v\n", cpk,csig)

	return cpk.VerifyBytes([]byte(msg), csig)
}
