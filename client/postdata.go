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
	//"reflect"
	"strconv"
)

type TemplMessage struct {
	Type string `json:"type"`
	TID  string `json:"tid"`
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

/*
var (
	data TemplMessage
	//sdata *string
	//pdata *PostMessage
)
*/
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
		Sender: string(lib.Kid()),
		Data:   data,
	}
	urldata, err := json.Marshal(*sigdata)
	//fmt.Printf("marshal data:%s\n", urldata)
	if err != nil {
		fmt.Printf("marshal Err:%v\n", sigdata)
		return nil, err
	}
	newdata := base64.URLEncoding.EncodeToString(urldata)

	return &newdata, nil
}

func unpackTx(msg *string) {
	newdata, ok := base64.URLEncoding.DecodeString(*msg)
	if ok != nil {
		fmt.Printf("Unable to decode b64 data:%s\n", newdata)
		return
	}

	var txdata map[string]interface{}
	if err := json.Unmarshal([]byte(newdata), &txdata); err != nil {
		fmt.Printf("Unable to decode json data:%s\n", *msg)
		return
	}

	fmt.Printf("data:%+v\n", txdata["data"])
	fmt.Printf("sig:%T\n", txdata["sig"])
	if lib.CheckSig(txdata["sender"], txdata["data"], txdata["sig"]) {
		fmt.Printf("CheckSig ok:data:%s\n", txdata["data"])
	}
	return

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
	fmt.Printf("postdata:%s\n", body)

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
	file := flag.String("file", "../examples/templ_all.json", "which file to post")
	key := flag.String("key", "prvkey.json", "private key file to read")
	server := flag.String("server", "127.0.0.1", "server address")
	port := flag.Int("port", 26657, "server port")

	flag.Parse()
	var err error

	lib.Generate(*key)

	data, err := Load(*file)
	if err != nil {
		fmt.Printf("Load file error:%v\n", err)
		return
	}
	//fmt.Printf("data=%v\n", data)

	sdata, err := signdata(data)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		return
	}
	//fmt.Printf("signdata=%v\n", *sdata)

	//unpackTx(sdata)

	pdata, err := builddata(sdata)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		return
	}
	fmt.Printf("pdata=%+v\n", pdata)

	err = postdata(pdata, *server, *port)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		return
	}

}
