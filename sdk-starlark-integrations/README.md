# Using Starlark scripts for custom integrations

## Create custom integration

- Navigate to Account -> Custom integrations

- Click the "Add custom integration" button at the top right of the screen

![create custom integration](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_1.png?raw=true)

- Give the custom integration a name (this will be the source name e.g. custom_integration:my_integration_name)

- Optionally provide a description for the integration

- Optionally upload an Icon. This will appear in the "Custom integration" source column of the inventory. If no icon is provided a `</>` will appear as the source icon.

- Toggle the "Custom Integration Script" slider on

- Paste the starlark integration script into the "Custom integration script" text box

- Click the "Save" button at the top right of the screen

![configure custom integration](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_2.png?raw=true)

## Configure credentials

- Navigate to Credentials and click the "Add credential" button at the top right of the screen

![Add credential](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_3.png?raw=true)

- From the "Credential type" drop down menu select "Custom Integration Access Key Credential"

![select credential type](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_4.png?raw=true)

- Give the credential an appropriate name

- Provide the value assigned to the kwargs access_key argument used within the script in the "CustomIntegrationScript kwarg access_key" text box

- Provide the value assigned to the kwargs access_secret argument used within the script in the "CustomIntegrationScript kwarg access_secret" text box

![configure credential](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_5.png?raw=true)

## Create custom integration sync task



## Querying the data

