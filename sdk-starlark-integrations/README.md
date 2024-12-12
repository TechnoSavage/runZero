# Using Starlark scripts for custom integrations

## Create custom integration

- Navigate to "Account" -> "Custom integrations".

- Click the "Add custom integration" button at the top right of the page.

![create custom integration](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_1.png?raw=true)

- Give the custom integration a name (this will be the source name e.g. custom_integration:my_integration_name).

- Optionally provide a description for the integration.

- Optionally upload an Icon. This will appear in the "Custom integration" source column of the inventory. If no icon is provided a `</>` will appear as the source icon.

- Toggle the "Custom Integration Script" slider on.

- Paste the starlark integration script into the "Custom integration script" text box.

- Click the "Save" button at the top right of the page.

![configure custom integration](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_2.png?raw=true)

## Configure credentials

- Navigate to Credentials and click the "Add credential" button at the top right of the page.

![add credential](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_3.png?raw=true)

- From the "Credential type" drop down menu select "Custom Integration Access Key Credential".

![select credential type](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_4.png?raw=true)

- Give the credential an appropriate name.

- Provide the value assigned to the kwargs access_key argument used within the script in the "CustomIntegrationScript kwarg access_key" text box.

- Provide the value assigned to the kwargs access_secret argument used within the script in the "CustomIntegrationScript kwarg access_secret" text box.

- Click the "Save" button at the top right of the page.

![configure credential](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_5.png?raw=true)

## Create custom integration sync task

- Navigate to "Tasks".

- Click the "Integrate" button drop-down at the top right of the page and select "Custom Scripts".

![select task type](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_6.png?raw=true)

- Rename the sync task (optional).

- The new task defaults to "Create new script" allowing the user to paste their script directly into the Integration script text box. If using this approach also provide an appropriate name for the custom integration. This will create a corresponding custom integration under "Account" -> "Custom integrations" once the configuration is complete and the sync task is activated but skips the step to add an icon (which can be done later).

![configure sync task](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_7.png?raw=true)

- With a custom integration already defined, click the "Custom Integration" drop down menu and select the custom integration.

![select integration for task](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_8.png?raw=true)

- Click the "Custom Script Credential" drop down menu and select the appropriate credentials for the task.

- The drop down menu also provides an option to create a new credential which will populate text fields the mirror the steps in the above [Configure credentials](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/README.md#Configure-credentials) step.

![select credential for task](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_9.png?raw=true)

- Select the Explorer to execute the sync task from in the "Explorer" drop down menu.

- Select the site to populate the sync task results to in the "Site" drop down menu. Assets from the sync task that are merged to existing assets in the inventory will reflect the site of the original asset record; all other new (unmerged) asset records are populated to the selected site.

- Provide a description for the sync task (optional)

- Select the desired scheduling and recurring frequency for the sync task

- Click the "Activate Connection" button at the bottom right of the page.

![finalize task configuration](https://github.com/TechnoSavage/runZero/blob/main/sdk-starlark-integrations/img-resources/img_10.png?raw=true)

- The sync task and progress will be visible in the "Tasks" -> "Task overview" page.

## Querying the data

