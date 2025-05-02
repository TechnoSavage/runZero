# CLI Scanner usage examples

## Scan and upload to site in organization

```
sudo runzero scan <target ip or subnet> -r 1000 -v --api-key <organization key> --api-url https://console.rumble.run/api/v1.0 --upload --upload-site <site name>
```

## Read target file line by line to scan and upload (BaSH or similar)

```
while read -r line; do 
echo "Scanning ${line}..."; sudo runzero scan ${line} -r 20000 -v --api-key <organization key> --api-url https://console.runzero.com/api/v1.0/  --upload --upload-site "My Site Name"; 
done < target_list.txt
```