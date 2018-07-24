#!/bin/sh

curl "localhost:26657/status"

curl http://localhost:26657/broadcast_tx_commit?tx=\"hello\"

curl "http://localhost:26657/block?height=1"

curl http://localhost:26657/block_results?height=3

curl http://localhost:26657/blockchain?minHeight=1&maxHeight=4

curl http://localhost:26657/commit?height=3

curl http://localhost:26657/validators?height=2

curl http://localhost:26657/unconfirmed_txs?limit=100

curl "http://localhost:26657/tx_search?query=\"type='template'\"&prove=true"
curl "http://localhost:26657/tx_search?query=\"tx.hash='093D339C4C49B04197B402B21BBBF23805E01F49'\"&prove=true"

curl --data-binary '{"jsonrpc":"2.0","id":"anything","method":"broadcast_tx_commit","params": {"tx": "AQIDBA=="}}' -H 'content-type:text/plain;' http://localhost:26657

#{"params": {"tx": "{\"sig\": \"IDHqU0ChR0zSr0q0wJkY8FrHk4Lw+Plr7VQyhqMdL7Ve5/SIQeqSnuukfC8G+rduxt0+UcEjT+nc9kRUnZ+750ZXDV4N\", \"data\": \"ewoJInR5cGUiOiJ0ZW1wbGF0ZSIsCgkidG5hbWUiOiLpmJzlpJblv4PlhoXnp5Hpmo/orr8iLAoJInRpZCI6IkZXMjAxODA3MTYwNCIsCgkiY2F0ZWdvcnkiOiJGb2xsb3d1cFN1cnZleTpIZWFydERpc2Vhc2UiLAoJInRlbXBsYXRlIjpbCgkJeyJuYW1lIjoiZ2VuZXJhbCIsCgkJImFsaWFzIjoi5Z+65pys5L+h5oGvIiwKCQkiRElEIjoxLAoJCSJ0aWQiOiJGVzIwMTgwNzE2MDEiLAoJCSJyZXF1aXJlZCI6dHJ1ZQoJCX0sCgkJeyJuYW1lIjoiU21va2VIaXN0b3J5IiwKCQkiYWxpYXMiOiLlkLjng5/lj7IiLAoJCSJESUQiOjIsCgkJInRpZCI6IkZXMjAxODA3MTYwMiIsCgkJInJlcXVpcmVkIjp0cnVlCgkJfSwKCQl7Im5hbWUiOiJCbG9vZFJvdXRpbmVFeGFtaW5hdGlvbiIsCgkJImFsaWFzIjoi6KGA5bi46KeEIiwKCQkiRElEIjozLAoJCSJ0aWQiOiJGVzIwMTgwNzE2MDMiLAoJCSJyZXF1aXJlZCI6dHJ1ZQoJCX0KCV0KfQo=\", \"sender\": \"cf09b56c5cad90cb1d050a506f50663b13432043\"}"}, "jsonrpc": "2.0", "id": "anything", "method": "broadcast_tx_commit"}

