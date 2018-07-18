# Data encapsulation with signature

##Big picture
###The data exchange system has following key concepts:
template
data
contract
transaction
buyer
seller

the relationship is as flows:


##Data exchange
###We have two kind of data to be post:</br>
Plain Data </br>
Encrypted Data </br>

###Plain Data Exchange
For plain data, if data we assume to upload is:</br>
```
	{
		"type":"template",
		"tid":"FW2018071602",
		"category":"general",
		"template":[
			{"name":"Patientname",
			"alias":"姓名",
			"DID":1,
			"type":"string",
			"required":true
			},
		]
	}
```

So the data we send may be:</br>
```
{
	"sender":"886812acdf2...",
	"data":'{
		"type":"template",
		"tid":"FW2018071602",
		"category":"general",
		"template":[
			{"name":"Patientname",
			"alias":"姓名",
			"DID":1,
			"type":"string",
			"required":true
			},
			]
		}',
	"sig":"9012387t5121..."
}
```
###Encrypt Data Exchange
Suppose the data to be encrypted is:
```
{
        "type":"data",
	"encode":"plain",
        "tid":"FW2018071601",
        "data":[
                {
			"DID":1,
                	"value":12.98
                },  
                {
			"DID":2,
                	"value":4.64
                },  
                {
                	"DID":3,
                	"value":123
                }
        ]
}
```
{
	"sender":"886812acdf2...",
	"data":'75969569870806'
	"sig":"9012387t5121..."
}
```

##Data encrypt and Decrypt
All data is encrypted with a symmetric cryptography, such as AES, however, the key of symmetric cryptography is protected with the pub key of the buyer, the seller 
