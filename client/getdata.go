package main

import (
	//lib "../lib"
	//"bytes"
	//"encoding/base64"
	//"encoding/hex"
	//"encoding/json"
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

func GetData(localpart string, server string, port int) ([]byte, error) {
	newurl := "http://" + server + ":" + strconv.Itoa(port) + "/" + localpart
	if *verbose {
		fmt.Printf("url=%s\n", newurl)
	}
	rsp, err := http.Get(newurl)
	if err != nil {
		fmt.Printf("Error: http get:%v, url:%s\n", err, newurl)
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
	//key := flag.String("key", "prvkey.json", "private key file to read")
	server := flag.String("server", "127.0.0.1", "server address")
	port := flag.Int("port", 26657, "server port")
	verbose = flag.Bool("v", false, "Verbose:default false")
	lurl := flag.String("lurl", "status", "local part of url to query")
	//mode := flag.String("mode", "plain", "unMarshal json data:plain")

	flag.Parse()
	var err error

	//err = lib.Generate(*key)
	if err != nil {
		fmt.Printf("Error:GetKey:%v\n", err)
		panic(2)
	}

	resp, err := GetData(*lurl, *server, *port)
	if err != nil {
		fmt.Printf("Error:post data:%v\n", err)
		return
	}
	fmt.Println(string(resp))
}
