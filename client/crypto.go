package main

import (
	lib "../lib"
	//"bytes"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	//"reflect"
)

var verbose *bool

type CipherMessage struct {
	Type   string `json:"cipher"`
	Cipher string `json:"data"`
}

type SignMessage struct {
	Sender string      `json:"sender"`
	Sig    string      `json:"sig"`
	Data   interface{} `json:"data"`
}

type TxMessage struct {
	Tx string `json:"tx"`
}

type PostMessage struct {
	Ver    string    `json:"jsonrpc"`
	Id     string    `json:"id"`
	Method string    `json:"method"`
	Params TxMessage `json:"params"`
}

func Load(filename string) (msg interface{}, err error) {
	err = nil
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error: read file%v\n", err)
		return
	}

	err = json.Unmarshal([]byte(data), &msg)
	if err != nil {
		fmt.Printf("Error: Unmarshal json:%v\n", err)
		return
	}
	return
}

func signdata(data interface{}) (*string, error) {
	msg, err := json.Marshal(data)
	if err != nil {
		fmt.Printf("Error:Marshal json error:%v\n", err)
		panic(2)
	}

	sigdata := &SignMessage{
		Sig:    lib.Sign(msg),
		Sender: hex.EncodeToString(lib.Getpubkey()),
		Data:   data,
	}

	urldata, err := json.Marshal(*sigdata)
	if err != nil {
		fmt.Printf("Error:Marshal json:%v\n", sigdata)
		return nil, err
	}
	if *verbose {
		fmt.Printf("marshal res:%s\n", urldata)
	}
	newdata := base64.URLEncoding.EncodeToString(urldata)

	return &newdata, nil
}

func main() {
	verbose = flag.Bool("v", false, "Verbose:default false")
	mode := flag.String("mode", "pub", "Task:pub(show pubkey),pubenc(using pubkey to encode data),symmenc(use symmetric cipher to encode plaintext),symmdec(use symmetric cipher to decode plaintext),prvdec(using pubkey to decode data)")
	key := flag.String("key", "prvkey.json", "private key file to read")
	pubkey := flag.String("pubkey", "", "receiver's pubkey")
	plain := flag.String("plain", "", "data to encode using pubkey")
	cipher := flag.String("cipher", "", "data to decode using symmetric or prvkey")
	secret := flag.String("secret", "", "symmantric key to encipher|decipher")

	flag.Parse()

	var err error

	if err != nil {
		fmt.Printf("Error:GetKey:%v\n", err)
		panic(2)
	}

	switch *mode {
	case "key":
		keypath, err := lib.Generate(*key, true)
		if err != nil {
			fmt.Printf("Generate key error:%v\n", err)
			return
		}
		fmt.Print(keypath)
		return
	case "pub":
		_, err = lib.Generate(*key, false)
		fmt.Print(hex.EncodeToString(lib.Getpubkey()))
		return
	case "symmenc":
		bytesec, err := hex.DecodeString(*plain)
		if err != nil {
			fmt.Printf("hex decode error:%v\n", err)
			return
		}
		secret, cipher := lib.NewCipher(bytesec)
		fmt.Printf("Secret:%s\n", secret)
		//fmt.Printf("Cipher:%s\n", hex.EncodeToString(cipher))
		//fmt.Printf("Secret:%s\n", strsecret)
		fmt.Printf("Cipher:%s\n", cipher)
	case "symmdec":
		bytesec, err := hex.DecodeString(*secret)
		if err != nil {
			fmt.Printf("hex decode error:%v\n", err)
			return
		}
		bytecipher, err := hex.DecodeString(*cipher)
		if err != nil {
			fmt.Printf("hex decode error:%v\n", err)
			return
		}
		newplain, err := lib.DeCipher(bytecipher, bytesec)
		if err != nil {
			fmt.Printf("Decipher error:%v\n", err)
			return
		}
		fmt.Printf("%s", newplain)
	case "pubenc":
		if *plain == "" {
			fmt.Println("Error:Must provide data to be encoded!")
			return
		}
		if *pubkey == "" {
			fmt.Println("Error:Must provide pubkey to encod data!")
			return
		}
		lib.ImportReceiver(*pubkey)
		cipher, err := lib.SendReceiver([]byte(*plain))
		if err != nil {
			fmt.Printf("Error:Encode with pubkey:%v\n", err)
			return
		}
		cipherstr := hex.EncodeToString(cipher)
		fmt.Printf("%s", cipherstr)
		/*
			//test code
			fmt.Printf("cipher:%v\n", cipher)
			_,err = lib.Generate(*key)
			if err != nil {
				fmt.Printf("load key file error:%v\n", err)
				return
			}
			bytecipher, err := hex.DecodeString(cipherstr)
			if err != nil {
				fmt.Printf("hex decode error:%v\n", err)
				return
			}
			fmt.Printf("\nbytecipher:%v\n", bytecipher)
			newplain, err := lib.PrvDecrypt(bytecipher)
			if err != nil {
				fmt.Printf("Decipher error:%v\n", err)
				return
			}
			fmt.Printf("Plain:%s\n", newplain)
		*/
		return
	case "prvdec":
		if *cipher == "" {
			fmt.Println("Error:Must provide data to be decoded!")
			return
		}
		if *key == "" {
			fmt.Println("Error:Must provide private keyfile!")
			return
		}
		_, err = lib.Generate(*key, false)
		if err != nil {
			fmt.Printf("load key file error:%v\n", err)
			return
		}
		bytecipher, err := hex.DecodeString(*cipher)
		if err != nil {
			fmt.Printf("hex decode error:%v\n", err)
			return
		}
		//fmt.Printf("bytecipher:%v", bytecipher)
		newplain, err := lib.PrvDecrypt(bytecipher)
		if err != nil {
			fmt.Printf("Decipher error:%v\n", err)
			return
		}
		fmt.Printf("%s", newplain)
	default:
		fmt.Printf("Error:Mode:%s\n", *mode)
		return
	}
}
