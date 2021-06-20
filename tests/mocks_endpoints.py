MockEndpoint1UUID = "8bcca2cf-e166-4638-992d-d6e901c6e93a"
MockEndpoint2UUID = "ac8348d4-9e48-464e-ac6c-e7a76007e7b3"

mock_endpoints_responses = {
    "/1.0.0/inventory/endpoints/customeruuid/": {
        "GET": {
            "json": {
                "endpointlist": [
                ]
            }
        }
    }
}
