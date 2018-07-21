package main

import (
	lib "../lib"
	"flag"
	"fmt"
)

func main() {
	cmd := flag.String("cmd", "genkey", "task to be run:genkey,id,pub,sign")
	keypath := flag.String("keypath", "./prvkey.json", "where to read or generate prvkey")
	msg := flag.String("msg", "aGVsbG8gd29ybGQK", "data to be signed, data must be base64 encoded")
	flag.Parse()

	switch {
	case *cmd == "genkey":
		lib.Generate(*keypath)
	case *cmd == "id":
		lib.Generate(*keypath)
		Kid := lib.Kid()
		fmt.Printf("%s", Kid)
	case *cmd == "pub":
		lib.Generate(*keypath)
		pub := lib.Getpubkey()
		fmt.Printf("%s", pub)
	case *cmd == "sign":
		if *msg == "" {
			fmt.Println("Must provide a base64 encoded string using -msg")
			panic(1)
		}
		lib.Generate(*keypath)
		sig := lib.Sign(*msg)
		fmt.Printf("%s", sig)
	}
}
