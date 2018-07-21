package main

import (
	//"fmt"
	"github.com/tendermint/tendermint/abci/server"
	"github.com/tendermint/tendermint/abci/types"
	cmn "github.com/tendermint/tendermint/libs/common"
	"github.com/tendermint/tendermint/libs/log"
	"os"
)

var logger log.Logger

func main() {
	logger = log.NewTMLogger(log.NewSyncWriter(os.Stdout))

	var app types.Application
	app = NewKVStoreApplication()

	//srv, err := server.NewServer("127.0.0.1:26658" /*flagAddress, flagAbci,*/, "grpc", app)
	srv, err := server.NewServer("127.0.0.1:26658" /*flagAddress, flagAbci,*/, "socket", app)
	if err != nil {
		os.Exit(1)
	}
	srv.SetLogger(logger.With("module", "abci-server"))
	if err := srv.Start(); err != nil {
		os.Exit(2)
	}

	// Wait forever
	cmn.TrapSignal(func() {
		// Cleanup
		srv.Stop()
	})
	os.Exit(0)
}
