import logging

import azure.functions as func

app = func.FunctionApp()


# @app.function_name(name="HttpTrigger1")  # default to function name
# @permission_decorator()
@app.route(route="HttpExample", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@app.queue_output(
    arg_name="outmsg",
    queue_name="test-outqueue-func-xiang",
    connection="AzureWebJobsStorage",
)
def http_trigger(
    req: func.HttpRequest,
    outmsg: func.Out[func.QueueMessage],
) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    headers = dict(req.headers)

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        outmsg.set(name)
        return func.HttpResponse(f"Hello, {name}. {headers}")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )


@app.route(
    route="http_trigger_with_blob_input/{blob_name}",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=["GET"],
)
@app.blob_input(
    arg_name="inputblob",
    path="samples-workitems/{blob_name}",
    connection="AzureWebJobsStorage",
)
def http_trigger_with_blob_input(
    req: func.HttpRequest,
    inputblob: str,
) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    headers = dict(req.headers)
    print(f"=== inputblob: {inputblob}")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if inputblob:
        return func.HttpResponse(f"Hello, {name}. with blob : {inputblob},")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )


@app.blob_trigger(
    arg_name="inblob", path="samples-workitems/{name}", connection="AzureWebJobsStorage"
)
@app.queue_output(
    arg_name="outmsg",
    queue_name="test-outqueue-func-xiang",
    connection="AzureWebJobsStorage",
)
# @app.cosmos_db_output(
#     arg_name="outdocument",
#     database_name="my-database",
#     container_name="my-container",
#     connection="CosmosDbConnectionString",
# )
def blob_trigger_event_grid(
    inblob: func.InputStream,
    outmsg: func.Out[func.QueueMessage],
    # outdocument: func.Out[func.Document],
):
    logging.info("Python HTTP trigger function processed a request.")
    last_modified = inblob.blob_properties["LastModified"]
    blob_msg = f"{last_modified} {inblob.name}"
    # outdocument.set(func.Document.from_dict({"id": blob_msg}))
    outmsg.set(blob_msg)
