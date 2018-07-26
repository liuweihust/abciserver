package lib

import (
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/btcsuite/btcd/btcec"
	"github.com/btcsuite/btcd/chaincfg/chainhash"
	crypto "github.com/tendermint/tendermint/crypto"
	cmn "github.com/tendermint/tendermint/libs/common"
	"io/ioutil"
)

//type PubkeyType btcec.PublicKey
//type PrvkeyType btcec.PrivateKey
type SigType btcec.Signature
type PrvKey struct {
	PrivKey []byte `json:"priv_key"` // our priv key
}

const SecretLen = 32

var pubkey, receiver *btcec.PublicKey
var prvkey *btcec.PrivateKey
var err error

func LoadOrGenPrvKey(filePath string) error {
	if cmn.FileExists(filePath) {
		err := LoadPrvKey(filePath)
		if err != nil {
			fmt.Printf("Loadkey error:%s\n", filePath)
			return err
		}
		return nil
	}
	return genPrvKey(filePath)
}

func LoadPrvKey(filePath string) error {
	jsonBytes, err := ioutil.ReadFile(filePath)
	if err != nil {
		return err
	}
	nodeKey := new(PrvKey)
	err = json.Unmarshal(jsonBytes, nodeKey)
	if err != nil {
		fmt.Printf("Error reading PrvKey from %v: %v", filePath, err)
		return nil
	}

	prvkey, pubkey = btcec.PrivKeyFromBytes(btcec.S256(), nodeKey.PrivKey)
	return nil
}

func genPrvKey(filePath string) error {
	var err error
	prvkey, err = btcec.NewPrivateKey(btcec.S256())
	if err != nil {
		return err
	}

	nodeKey := &PrvKey{
		PrivKey: prvkey.Serialize(),
	}

	jsonBytes, err := json.Marshal(nodeKey)
	if err != nil {
		fmt.Printf("Unmarshal key error:%v\n", err)
		return err
	}
	err = ioutil.WriteFile(filePath, jsonBytes, 0600)
	if err != nil {
		fmt.Printf("Write key file error:%v\n", err)
		return err
	}
	return nil
}

func Generate(filePath string) error {
	err = LoadOrGenPrvKey(filePath)
	if err != nil {
		return err
	}
	return nil
}

func Getpubkey() []byte {
	return prvkey.PubKey().SerializeCompressed()
}

func Sign(msg []byte) string {
	messageHash := chainhash.DoubleHashB([]byte(msg))
	signature, err := prvkey.Sign(messageHash)
	if err != nil {
		fmt.Printf("sign error:%v\n", prvkey)
		panic(err)
	}
	encodeString := base64.StdEncoding.EncodeToString(signature.Serialize())
	return encodeString
}

//If sig match pubkey and msg, will return true, else return false
func CheckSig(pubkeystr string, msgstr string, sigstr string) bool {
	var err error

	decodeBytes, err := base64.StdEncoding.DecodeString(sigstr)
	if err != nil {
		fmt.Printf("Fail to base64 decode sig:%s\n", sigstr)
		return false
	}
	sig, err := btcec.ParseSignature(decodeBytes, btcec.S256())
	if err != nil {
		fmt.Printf("Fail to build signature:%v\n", decodeBytes)
		return false
	}

	decode, err := hex.DecodeString(pubkeystr)
	if err != nil {
		fmt.Printf("Fail to hex decode pubkey:%v\n", pubkeystr)
		return false
	}
	pubkey, err = btcec.ParsePubKey(decode, btcec.S256())
	if err != nil {
		fmt.Printf("Fail to parse pubkey:%v\n", pubkey)
		return false
	}

	messageHash := chainhash.DoubleHashB([]byte(msgstr))
	return sig.Verify(messageHash, pubkey)
}

func NewCipher(plaintext []byte) ([]byte, []byte) {
	secret := crypto.CRandBytes(SecretLen)
	ciphertext := crypto.EncryptSymmetric(plaintext, secret)
	return secret, ciphertext
}

func DeCipher(ciphertext []byte, secret []byte) ([]byte, error) {
	plaintext, err := crypto.DecryptSymmetric(ciphertext, secret)
	if err != nil {
		fmt.Printf("Marshal error:%v\n", err)
		return nil, err
	}
	return plaintext, nil
}

func ImportReceiver(pubstr string) error {
	decode, err := hex.DecodeString(pubstr)
	if err != nil {
		return err
	}
	receiver, err = btcec.ParsePubKey(decode, btcec.S256())
	if err != nil {
		return err
	}

	return err
}

func SendReceiver(plaintext []byte) ([]byte, error) {
	return PubEncrypt(plaintext, receiver)
}

func PubEncrypt(plaintext []byte, pubkey *btcec.PublicKey) ([]byte, error) {
	return nil, nil
}

func PrvDecrypt(ciphertext []byte, prvkey btcec.PrivateKey) ([]byte, error) {
	return nil, nil
}
