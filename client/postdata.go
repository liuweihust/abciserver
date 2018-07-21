package main

import (
	lib "../lib"
	"bytes"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
)

type TemplMessage struct {
	Type string `json:"type"`
	TID  string `json:"tid"`
}

type SignMessage struct {
	Sender string       `json:"sender"`
	Sig    string       `json:"sig"`
	Data   TemplMessage `json:"data"`
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

var (
	data  TemplMessage
	sdata *string
	pdata *PostMessage
)

func Load(filename string) (msg TemplMessage, err error) {
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

func signdata(data TemplMessage) (*string, error) {
	msg, err := json.Marshal(data)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		panic(2)
	}

	sigdata := &SignMessage{
		Sig:    lib.Sign(string(msg)),
		Sender: string(lib.Kid()),
		Data:   data,
	}
	urldata, err := json.Marshal(*sigdata)
	if err != nil {
		fmt.Printf("marshal Err:%v", sigdata)
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
		panic(err)
	}
	defer rsp.Body.Close()
	body_byte, err := ioutil.ReadAll(rsp.Body)
	if err != nil {
		panic(err)
	}
	fmt.Println(string(body_byte))

	return nil
}

func main() {
	file := flag.String("file", "../examples/templ_all.json", "which file to post")
	key := flag.String("key", "prvkey.json", "private key file to read")
	server := flag.String("server", "127.0.0.1", "server address")
	port := flag.Int("port", 26657, "server port")

	flag.Parse()
	var err error

	lib.Generate(*key)

	data, err = Load(*file)
	if err != nil {
		fmt.Printf("Load file error:%v\n", err)
		panic(1)
	}

	sdata, err = signdata(data)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		panic(3)
	}
	pdata, err = builddata(sdata)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		panic(3)
	}

	postdata(pdata, *server, *port)
}
