# Kismet starlark integration for runZero

Custom integration designed to pull asset information from a specified data source in Kismet.

## Kismet API Docs

- Kismet API Reference: https://www.kismetwireless.net/docs/api/rest_like/

- Kismet Docs: https://www.kismetwireless.net/docs/readme/intro/kismet/

## Configuration

`KISMET_BASE_URL` - The domain or IP of the Kismet web server e.g. http://<ip address>:2501

`client_secret` - The Cookie for the Kismet API.

## Getting Started

- Clone this repository

```
git clone https://github.com/TechnoSavage/runZero.git
```

# Important

For runZero to merge asset data from Snipe-IT to existing assets there must be a common matching asset attribute and field between what is reported by Snipe-IT and what can be found in the runZero asset record. A MAC address field in Snipe-IT is a recommended method. Snipe-IT has a default fieldset called 'Asset with MAC Address' that will serve this purpose. This script in its current form expects this field to be present for merge logic to work. The user is free to define and utilize other fields/attributes for this purpose as well (see SDK documentation).

New assets created by the integration that do not have MAC address (or other merge attributes) associated, such as the Network TAP example, will continue to be updated by subsequent sync tasks.