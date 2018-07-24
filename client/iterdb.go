package main

import (
	//"bytes"
	//"encoding/base64"
	//"encoding/json"
	"encoding/binary"
	"flag"
	"fmt"
	bs "github.com/tendermint/tendermint/blockchain"
	dbm "github.com/tendermint/tendermint/libs/db"
	"github.com/tendermint/tendermint/state"
	//"io/ioutil"
	//"net/http"
	//"strconv"
	//"path/filepath"
	//cmn "github.com/tendermint/tendermint/libs/common"
)

func myiter() {
	path := flag.String("path", "/tmp/testleveldb", "data path")
	flag.Parse()

	db := dbm.NewDB("test", "goleveldb", *path)
	defer db.Close()
	/*
		key := []byte("abc")
		value := []byte("hello")
		db.Set(key, value)

		key = []byte("def")
		value = []byte("world")
		db.Set(key, value)

		getvalue := db.Get(key)
		fmt.Printf("key=%s,Get value=%s\n", key, getvalue)
	*/

	start := make([]byte, 8)
	binary.BigEndian.PutUint64(start, uint64(0))
	var itr dbm.Iterator = db.Iterator(start, nil)
	defer itr.Close()

	for ; itr.Valid(); itr.Next() {
		k, v := itr.Key(), itr.Value()
		fmt.Printf("key(%s) value(%s)\n", k, v)
	}
}

func main() {
	path := flag.String("path", "/tmp/testleveldb", "data path")
	flag.Parse()

	statedb := dbm.NewDB("state", "goleveldb", *path)
	defer statedb.Close()
	state := state.LoadState(statedb)
	fmt.Printf("state:%+v\n", state)

	bsdb := dbm.NewDB("blockstore", "goleveldb", *path)
	defer bsdb.Close()
	//fmt.Printf("bsdb:%+v\n", bsdb)
	bs := bs.NewBlockStore(bsdb)
	//fmt.Printf("blockstore:%+v\n", bs)

	height := bs.Height()
	//fmt.Printf("height:%d\n", height)
	var i int64
	for i = 0; i < height; i++ {
		block := bs.LoadBlock(i)
		//fmt.Printf("[%d]:%+v\n", i, block)
		if block == nil {
			fmt.Printf("Height:%d:nil block\n", i)
			continue
		}
		header := block.Header
		if header == nil {
			fmt.Printf("Height:%d:nil header\n", i)
			continue
		}
		fmt.Printf("Height:%d tx num:%d\n", i, header.NumTxs)
		data := block.Data
		//fmt.Printf("data type:%T", data)
		if header.NumTxs <= 0 {
			continue
		}

		//fmt.Printf("[data===%+v\n", *data)
		for j, d := range data.Txs {
			fmt.Printf("	TX%d:%+s\n", j, string(d))
		}
	}
}
