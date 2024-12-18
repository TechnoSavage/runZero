# Using custom SDK scripts for custom integrations

## Create custom integration

![create custom integration](https://github.com/TechnoSavage/runZero/blob/main/sdk-sample-scripts/img-resources/img_1.png?raw=true)

- Navigate to "Account" -> "Custom integrations".

- Click the "Add custom integration" button at the top right of the page.

![add custom integration details](https://github.com/TechnoSavage/runZero/blob/main/sdk-sample-scripts/img-resources/img_2.png?raw=true)

- Give the custom integration a name (this will be the source name e.g. custom_integration:my_integration_name).

- Provide a description for the integration (optional).

- Upload an icon (optional). This will appear in the "Custom integration" source column of the inventory. If no icon is provided a `</>` will appear as the source icon.

- Click the "Save" button at the top right of the page.

## Create API Client

![create client](https://github.com/TechnoSavage/runZero/blob/main/sdk-sample-scripts/img-resources/img_3.png?raw=true)

- Navigate to "Account" -> "API clients.

- Click the "Register New API Client" button at the top right of the page.

![name client key and secret](https://github.com/TechnoSavage/runZero/blob/main/sdk-sample-scripts/img-resources/img_4.png?raw=true)

- Provide an application name for the client in the pop up.

![copy client key and secret](https://github.com/TechnoSavage/runZero/blob/main/sdk-sample-scripts/img-resources/img_5.png?raw=true)

- Copy the Client ID value to the "RUNZERO_CLIENT_ID" variable in the appropriate .env file for the custom integration script.

- Copy the Client Secret value to the "RUNZERO_CLIENT_SECRET" variable in the appropriate .env file for the custom integration script.

- Click "Done" in the lower right of the pop up (the client secret cannot be shown again after this action).

## Finish adding values to the .env file for the script

## Executing the script

- 

- The sync task and progress will be visible in the "Tasks" -> "Task overview" page.

## Querying the data

- Custom integration sources can be queried using the `custom_integration` keyword followed by the source name as defined in the [Create custom integration](https://github.com/TechnoSavage/runZero/blob/main/sdk-sample-scripts/README.md#Create-custom-integration) step. E.g. `custom_integration:snipe-it`

- Custom integration attributes can be queried just like any other integration attribute. Custom integration sources with have the `.custom` suffix in the keyword. For example, a custom integration called "snipe-it" that reports an asset attribute of "deviceType" would have a keyword like the following which shows a reported value of "WAP" `@snipe-it.custom.deviceType:="WAP"`.

## Scheduling scripts with Cron