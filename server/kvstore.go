package main

import (
	lib "../lib"
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"

	"github.com/tendermint/tendermint/abci/example/code"
	"github.com/tendermint/tendermint/abci/types"
	cmn "github.com/tendermint/tendermint/libs/common"
	dbm "github.com/tendermint/tendermint/libs/db"
)

type TxMessage struct {
	Sender string          `json:"sender"`
	Sig    string          `json:"sig"`
	Data   json.RawMessage `json:"data"`
}

var (
	stateKey        = []byte("stateKey")
	kvPairPrefixKey = []byte("kvPairKey:")
)

type State struct {
	db      dbm.DB
	Size    int64  `json:"size"`
	Height  int64  `json:"height"`
	AppHash []byte `json:"app_hash"`
}

var MapKeys = []string{"type", "tid", "did", "cid", "sid", "category"}

func loadState(db dbm.DB) State {
	stateBytes := db.Get(stateKey)
	var state State
	if len(stateBytes) != 0 {
		err := json.Unmarshal(stateBytes, &state)
		if err != nil {
			panic(err)
		}
	}
	state.db = db
	return state
}

func saveState(state State) {
	stateBytes, err := json.Marshal(state)
	if err != nil {
		panic(err)
	}
	state.db.Set(stateKey, stateBytes)
}

func prefixKey(key []byte) []byte {
	return append(kvPairPrefixKey, key...)
}

//---------------------------------------------------

var _ types.Application = (*KVStoreApplication)(nil)

type KVStoreApplication struct {
	types.BaseApplication

	state State
}

func NewKVStoreApplication() *KVStoreApplication {
	state := loadState(dbm.NewMemDB())
	return &KVStoreApplication{state: state}
}

func (app *KVStoreApplication) Info(req types.RequestInfo) (resInfo types.ResponseInfo) {
	return types.ResponseInfo{Data: fmt.Sprintf("{\"size\":%v}", app.state.Size)}
}

func (app *KVStoreApplication) DeliverTx(tx []byte) types.ResponseDeliverTx {
	var key, value []byte
	parts := bytes.Split(tx, []byte("="))
	if len(parts) == 2 {
		key, value = parts[0], parts[1]
	} else {
		key, value = tx, tx
	}
	app.state.db.Set(prefixKey(key), value)
	app.state.Size += 1
	var txdata TxMessage
	if err := json.Unmarshal(tx, &txdata); err != nil {
		logger.Error("unable to parse txdata:", "error", err, "data", fmt.Sprintf("%s", txdata))
		return types.ResponseDeliverTx{Code: code.CodeTypeEncodingError, Tags: nil}
	}

	var data map[string]interface{}
	if err := json.Unmarshal(txdata.Data, &data); err != nil {
		logger.Error("unable to parse txdata:", "error", err, "data", txdata)
		return types.ResponseDeliverTx{Code: code.CodeTypeEncodingError, Tags: nil}
	}

	var tags cmn.KVPairs

	for _, v := range MapKeys {
		tif, present := data[v]
		if present {
			tvalue, ok := tif.(string)
			if ok {
				tags = append(tags, cmn.KVPair{[]byte(v), []byte(tvalue)})
			}
		}
	}
	logger.Info(fmt.Sprintf("DeliverTx:%s", tags))
	return types.ResponseDeliverTx{Code: code.CodeTypeOK, Tags: tags}
}

func (app *KVStoreApplication) CheckTx(tx []byte) types.ResponseCheckTx {
	var txdata TxMessage
	if err := json.Unmarshal(tx, &txdata); err != nil {
		logger.Error("Unable to decode json data")
		return types.ResponseCheckTx{Code: code.CodeTypeEncodingError}
	}

	if lib.CheckSig(txdata.Sender, string(txdata.Data), txdata.Sig) {
		logger.Info(fmt.Sprintf("CheckSig ok:%v", string(txdata.Data)))
	} else {
		logger.Info("CheckSig failed:data\n")
		return types.ResponseCheckTx{Code: code.CodeTypeEncodingError}
	}

	return types.ResponseCheckTx{Code: code.CodeTypeOK}
}

func (app *KVStoreApplication) Commit() types.ResponseCommit {
	// Using a memdb - just return the big endian size of the db
	appHash := make([]byte, 8)
	binary.PutVarint(appHash, app.state.Size)
	app.state.AppHash = appHash
	app.state.Height += 1
	saveState(app.state)
	return types.ResponseCommit{Data: appHash}
}

func (app *KVStoreApplication) Query(reqQuery types.RequestQuery) (resQuery types.ResponseQuery) {
	fmt.Printf("query:%+v\n", reqQuery)
	if reqQuery.Prove {
		value := app.state.db.Get(prefixKey(reqQuery.Data))
		resQuery.Index = -1 // TODO make Proof return index
		resQuery.Key = reqQuery.Data
		resQuery.Value = value
		if value != nil {
			resQuery.Log = "exists"
		} else {
			resQuery.Log = "does not exist"
		}
		return
	} else {
		value := app.state.db.Get(prefixKey(reqQuery.Data))
		resQuery.Value = value
		if value != nil {
			resQuery.Log = "exists"
		} else {
			resQuery.Log = "does not exist"
		}
		return
	}
}
