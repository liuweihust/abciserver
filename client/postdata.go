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

func postdata(data *PostMessage, server string, port int) ([]byte, error) {
	body := new(bytes.Buffer)
	json.NewEncoder(body).Encode(*data)

	newurl := "http://" + server + ":" + strconv.Itoa(port)

	rsp, err := http.Post(newurl, "content-type:text/plain;", body)
	if err != nil {
		return nil, err
	}
	defer rsp.Body.Close()
	body_byte, err := ioutil.ReadAll(rsp.Body)
	if err != nil {
		return nil, err
	}

	return body_byte, nil
}

func main() {
	file := flag.String("file", "../examples/data_general.json", "which file to post")
	key := flag.String("key", "prvkey.json", "private key file to read")
	server := flag.String("server", "127.0.0.1", "server address")
	port := flag.Int("port", 26657, "server port")
	cipher := flag.String("cipher", "plain", "whether to encipher data,options:plain,symm,pubenc")
	pubkey := flag.String("pubkey", "", "receiver's pubkey")
	mode := flag.String("mode", "postdata", "Task:postdata,pub(show pubkey),pubenc(using pubkey to encode data)")
	verbose = flag.Bool("v", false, "Verbose:default false")
	//plain := flag.String("plain", "", "data to encode using pubkey")

	flag.Parse()

	var err error

	_, err = lib.Generate(*key, false)
	if err != nil {
		fmt.Printf("Error:GetKey:%v\n", err)
		panic(2)
	}

	switch *mode {
	/*
		case "pub":
			fmt.Print(hex.EncodeToString(lib.Getpubkey()))
			return
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
			fmt.Printf("%s", hex.EncodeToString(cipher))
			return
	*/
	case "postdata":
	default:
		fmt.Printf("Error:Mode:%s\n", *mode)
		return
	}

	data, err := Load(*file)
	dataf, ok := data.(map[string]interface{})
	if !ok {
		fmt.Printf("Error:Load file:%v\n", err)
		return
	}
	if *verbose {
		fmt.Printf("data[data]=%v\n", dataf["data"])
	}
	switch *cipher {
	case "symm":
		msg, err := json.Marshal(dataf["data"])
		if err != nil {
			fmt.Printf("Error:Marshal json:%v\n", err)
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
			fmt.Println("Error:Using pubkey enciper must provide pubkey")
			return
		}
		lib.ImportReceiver(*pubkey)

		msg, err := json.Marshal(dataf["data"])
		if err != nil {
			fmt.Printf("Error:Marshal json:%v\n", err)
			panic(2)
		}

		cipher, err := lib.SendReceiver(msg)
		if err != nil {
			fmt.Printf("Error:encode with pubkey:%v\n", err)
			panic(2)
		}
		dataf["encode"] = "pubkey"
		dataf["data"] = hex.EncodeToString(cipher)
		/*
			//Blow code will decode the cipher encoded by pubkey
			decipher, err := lib.PrvDecrypt(cipher)
			if err != nil {
				fmt.Printf("Error:Prv Decipher:%v\n", err)
				panic(2)
			}
			fmt.Printf("PrvDecrypt:%s\n", decipher)
			fmt.Printf("bytes equal:%v\n", bytes.Compare(msg, decipher))
		*/
	case "plain":
	default: //switch *cipher
		fmt.Println("Error:Cipher mode")
		return
	}

	sdata, err := signdata(dataf)
	if err != nil {
		fmt.Printf("Error:Sign data:%v\n", err)
		return
	}
	if *verbose {
		fmt.Printf("signdata=%v\n", *sdata)
	}

	pdata, err := builddata(sdata)
	if err != nil {
		fmt.Printf("Error:Build data:%v\n", err)
		return
	}
	if *verbose {
		fmt.Printf("pdata=%+v\n", pdata)
	}
	resp, err := postdata(pdata, *server, *port)
	if err != nil {
		fmt.Printf("Error:post data:%v\n", err)
		return
	}
	if *verbose {
		fmt.Println(string(resp))
	}
}
