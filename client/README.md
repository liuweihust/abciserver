# Data encapsulation with signature

###We have two kind of data to be post:</br>
Plain Data </br>
Encrypted Data </br>


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
