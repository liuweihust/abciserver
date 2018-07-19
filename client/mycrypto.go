package main

import (
	"encoding/base64"
	"flag"
	"fmt"
	//crypto "github.com/tendermint/tendermint/crypto"
	"github.com/tendermint/tendermint/p2p"
)

var prvkey *p2p.NodeKey
var err error

func generate(filePath string) error {
	prvkey, err = p2p.LoadOrGenNodeKey(filePath)
	if err != nil {
		return err
	}
	return nil
}

func kid() {
	fmt.Println(prvkey.ID())
}

func getpubkey() {
	fmt.Println(prvkey.PubKey())
}

func Sign(msg string) {
	/* base64 encoding, maybe use in future
	fmt.Println(encodeString)
	*/

	decodeBytes, err := base64.StdEncoding.DecodeString(msg)

	signature, err := prvkey.PrivKey.Sign(decodeBytes)
	if err != nil {
		panic(err)
	}
	encodeString := base64.StdEncoding.EncodeToString(signature.Bytes())
	fmt.Println(encodeString)
}

func main() {
	cmd := flag.String("cmd", "genkey", "task to be run:genkey,id,pub,sign")
	keypath := flag.String("keypath", "./prvkey.json", "where to read or generate prvkey")
	msg := flag.String("msg", "aGVsbG8gd29ybGQK", "data to be signed, data must be base64 encoded")
	flag.Parse()

	switch {
	case *cmd == "genkey":
		generate(*keypath)
	case *cmd == "id":
		generate(*keypath)
		kid()
	case *cmd == "pub":
		generate(*keypath)
		getpubkey()
	case *cmd == "sign":
		if *msg == "" {
			fmt.Println("Must provide a base64 encoded string using -msg")
			panic(1)
		}
		generate(*keypath)
		Sign(*msg)
	}
}
