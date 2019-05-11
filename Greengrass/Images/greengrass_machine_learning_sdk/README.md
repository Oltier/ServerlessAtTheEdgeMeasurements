# Greengrass Machine Learning Python SDK
The Greengrass Machine Learning SDK provides an interface to send inference requests and receive results.

## invoke_inference_service(**kwargs)

After deploying a Greengrass Machine Learning connector to a Greengrass core, a client lambda uses this API to get inferences from the model at the service name you specified while adding the connector to your Greengrass group.

### Request Syntax
```python
response = client.invoke_inference_service(
    AlgoType='string',
    ServiceName='string',
    ContentType='string',
    Accept='string',
    Body=b'bytes'|file
)
```

#### Parameters
* **AlgoType** (string): *[Required]* The name of the inference algorithm type. You can find the value to be passed in on Greengrass Machine Learning online documentation.
* **ServiceName** (string): *[Required]* The name of the local inference service when the connector was added to your Greengrass group.
* **Body** (bytes or seekable file-like object): *[Required]* Provides input data, in the format specified in the **ContentType** request header. All of the data in the body will be passed to the model.
* **ContentType** (string): *[Required]* The MIME type of the input dat in the **Body** field.
* **Accept** (string): *[Optional]* The desired MIME type of the inference in the response.

### Response type
dict

### Response Syntax
```python
{
    'Body': StreamingBody(),
    'ContentType': 'string'
}
```

#### Response Structure
* **Body** (StreamingBody): Includes the inference result provided by the model.
* **ContentType** (string): The MIME type of the inference result returned in the **Body** field.
