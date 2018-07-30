#!/bin/sh

go build -gcflags "-N -l" iterdb.go
go build -gcflags "-N -l" postdata.go
go build -gcflags "-N -l" getdata.go
go build -gcflags "-N -l" crypt.go
