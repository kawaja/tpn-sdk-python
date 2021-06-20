MockDatacentresDC1UUID = '21ca83fb-a506-48ec-8439-58a1342703db'
MockDatacentresDC2UUID = 'd1125a6c-b7b9-4156-9c6b-a42aa9cced04'

mock_datacentres_responses = {
    "/1.0.0/inventory/datacenters": {
        ('default', 'GET'): {
            "json": {
                "datacenters": [
                    {
                        "cityname": "Melbourne",
                        "countryname": "Australia",
                        "datacentercode": "AMLS",
                        "datacentername": "Melbourne (NextDC)",
                        "datacenteruuid": MockDatacentresDC1UUID,
                        "interfacetypes": [],
                        "location_provider_uuid":
                            "2aae4595-7b2c-4017-93b0-dd6e5734r355",
                        "operatorname": ""
                    },
                    {
                        "cityname": "Melbourne",
                        "countryname": "Australia",
                        "datacentercode": "AMEQ",
                        "datacentername": "Melbourne Equinix ME1",
                        "datacenteruuid": MockDatacentresDC2UUID,
                        "interfacetypes": [],
                        "location_provider_uuid":
                            "2aae7295-7b3c-4017-96b0-dd6e5734r344",
                        "operatorname": ""
                    }
                ]
            }
        }
    }
}
