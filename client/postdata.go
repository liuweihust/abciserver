package main

import (
	lib "../lib"
	"bytes"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	//"reflect"
	"strconv"
)

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
		fmt.Printf("error:%v\n", err)
		return
	}

	err = json.Unmarshal([]byte(data), &msg)
	if err != nil {
		fmt.Printf("Parse json error:%v\n", err)
		return
	}
	return
}

func signdata(data interface{}) (*string, error) {
	msg, err := json.Marshal(data)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		panic(2)
	}

	sigdata := &SignMessage{
		Sig:    lib.Sign(msg),
		Sender: hex.EncodeToString(lib.Getpubkey()),
		Data:   data,
	}

	urldata, err := json.Marshal(*sigdata)
	if err != nil {
		fmt.Printf("marshal Err:%v\n", sigdata)
		return nil, err
	}
	newdata := base64.URLEncoding.EncodeToString(urldata)

	return &newdata, nil
}

func builddata(sigmsg *string) (postdata *PostMessage, err error) {
	txdata := TxMessage{
		Tx: *sigmsg,
	}

	pdata := &PostMessage{
		Ver:    "2.0",
		Id:     "anything",
		Method: "broadcast_tx_commit",
		Params: txdata,
	}
	return pdata, nil
}

func postdata(data *PostMessage, server string, port int) error {
	body := new(bytes.Buffer)
	json.NewEncoder(body).Encode(*data)

	newurl := "http://" + server + ":" + strconv.Itoa(port)

	rsp, err := http.Post(newurl, "content-type:text/plain;", body)
	if err != nil {
		return err
	}
	defer rsp.Body.Close()
	body_byte, err := ioutil.ReadAll(rsp.Body)
	if err != nil {
		return err
	}
	fmt.Println(string(body_byte))

	return nil
}

func main() {
	file := flag.String("file", "../examples/data_general.json", "which file to post")
	key := flag.String("key", "prvkey.json", "private key file to read")
	server := flag.String("server", "127.0.0.1", "server address")
	port := flag.Int("port", 26657, "server port")
	cipher := flag.String("cipher", "pubkey", "whether to encipher data,options:plain,symm,pubkey")
	pubkey := flag.String("pubkey", "", "receiver's pubkey")
	mode := flag.String("mode", "postdata", "Task:postdata,pub(show pubkey)")

	flag.Parse()
	var err error

	err = lib.Generate(*key)
	if err != nil {
		fmt.Printf("GetKey error:%v\n", err)
		panic(2)
	}

	switch *mode {
	case "pub":
		fmt.Print(hex.EncodeToString(lib.Getpubkey()))
		return
	default:
	}

	data, err := Load(*file)
	dataf, ok := data.(map[string]interface{})
	if !ok {
		fmt.Printf("Load file error:%v\n", err)
		return
	}
	//fmt.Printf("data[data]=%v\n", dataf["data"])

	switch *cipher {
	case "symm":
		msg, err := json.Marshal(dataf["data"])
		if err != nil {
			fmt.Printf("Marshal error:%v\n", err)
			panic(2)
		}

		secret, cipher := lib.NewCipher(msg)
		strsecret := hex.EncodeToString(secret)
		dataf["encode"] = "plain"
		dataf["data"] = hex.EncodeToString(cipher)
		fmt.Printf("Secret:%s\n", strsecret)

		/*
			//Following lines check whether symmetric encipher,decipher works ok
			bytesec, err := hex.DecodeString(strsecret)
			if err != nil {
				fmt.Printf("hex decode error:%v\n", err)
				return
			}
			newplain, err := lib.DeCipher(cipher, bytesec)
			if err != nil {
				fmt.Printf("Decipher error:%v\n", err)
				return
			}
			fmt.Printf("bytes equal:%v\n", bytes.Compare(msg, newplain))
		*/
	case "pubkey":
		if (*pubkey) == "" {
			fmt.Println("Using pubkey enciper must provide pubkey")
			return
		}
		lib.ImportReceiver(*pubkey)

		msg, err := json.Marshal(dataf["data"])
		if err != nil {
			fmt.Printf("Marshal error:%v\n", err)
			panic(2)
		}

		cipher, err := lib.SendReceiver(msg)
		if err != nil {
			fmt.Printf("Marshal error:%v\n", err)
			panic(2)
		}
		dataf["encode"] = "pubkey"
		dataf["data"] = hex.EncodeToString(cipher)
		/*
			//Blow code will decode the cipher encoded by pubkey
			decipher, err := lib.PrvDecrypt(cipher)
			if err != nil {
				fmt.Printf("Prv Decipher error:%v\n", err)
				panic(2)
			}
			fmt.Printf("PrvDecrypt:%s\n", decipher)
			fmt.Printf("bytes equal:%v\n", bytes.Compare(msg, decipher))
		*/
	case "plain":
	default: //switch *cipher
		fmt.Println("Cipher mode Error")
		return
	}

	sdata, err := signdata(dataf)
	if err != nil {
		fmt.Printf("Sign data error:%v\n", err)
		return
	}
	//fmt.Printf("signdata=%v\n", *sdata)

	pdata, err := builddata(sdata)
	if err != nil {
		fmt.Printf("Build data error:%v\n", err)
		return
	}
	fmt.Printf("pdata=%+v\n", pdata)

	err = postdata(pdata, *server, *port)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		return
	}
}
