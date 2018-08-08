#!/bin/sh

#go build -gcflags "-N -l" iterdb.go
go build -gcflags "-N -l" postdata.go
go build -gcflags "-N -l" getdata.go
go build -gcflags "-N -l" crypto.go

install postdata getdata crypto $GOPATH/bin/
