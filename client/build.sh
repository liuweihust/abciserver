#!/bin/sh

go build -gcflags "-N -l" iterdb.go
go build -gcflags "-N -l" postdata.go
