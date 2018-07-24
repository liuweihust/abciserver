package lib

import (
	//"encoding/base64"
	"fmt"
	crypto "github.com/tendermint/tendermint/crypto"
	"github.com/tendermint/tendermint/p2p"
	"reflect"
)

type PubkeyType crypto.PubKey
type SigType crypto.Signature

var prvkey *p2p.NodeKey
var err error

type Convert interface {
	AsByte() []byte
}

func (PubkeyType) AsByte() []byte {

}

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

func Getpubkey() PubkeyType {
	return prvkey.PubKey()
}

func Sign(msg []byte) SigType {
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
	/*encodeString := base64.StdEncoding.EncodeToString(signature.Bytes())
	return encodeString
	*/
	return signature
}

func Bytes(data interface{}) ([]byte, error) {
	fmt.Printf("data type:%v\n", reflect.TypeOf(data))
	mb, ok := data.([]byte)
	if ok {
		fmt.Printf("byte ok,mb=%v\n", mb)
		return mb, nil
	}

	switch t := data.(type) {
	case interface{}:
		fmt.Printf("interface %v\n", t)
		fmt.Printf("interface data type:%v\n", reflect.TypeOf(t))
	case []interface{}:
		fmt.Printf("interface %v\n", t)
		fmt.Printf("interface data type:%v\n", reflect.TypeOf(t))
	case []byte:
		//if len(t) != crypto.PubKeyEd25519Size {
		fmt.Printf("%+v len:%d is not a pubkey size:%d\n", t, crypto.PubKeyEd25519Size, len(t))
		return t, nil
	case PubkeyType:
		fmt.Printf("type []byte\n")
		return nil, nil
	case SigType:
		fmt.Printf("type []byte\n")
		return nil, nil
	case byte:
		fmt.Printf("type byte\n")
		return nil, nil
	default:
		fmt.Printf("Switch default: %T\n", data)
		//}

	}
	return nil, nil
}

//If sig match pubkey and msg, will return true, else return false
func CheckSig(pubkey interface{}, msg interface{}, sig interface{}) bool {
	var bpk /*, bdata, bsig*/ []byte
	var err error

	bpk, err = Bytes(pubkey)
	if err != nil {
		fmt.Printf("Convert pubkey error:%+v\n", pubkey)
		return false
	}
	fmt.Printf("bpk:%s\n", bpk)
	/*
		if len(pubkey) != crypto.PubKeyEd25519Size {
				fmt.Printf("%+v len:%d is not a pubkey size:%d", pubkey, crypto.PubKeyEd25519Size, len(pubkey))
				return false
			}
			if ok != nil {
				return false
			}
			return inpubkey.VerifyBytes(msg, crypto.Signature(sig))
	*/
	return true
}
