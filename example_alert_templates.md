[Alert object and field reference](https://www.runzero.com/docs/creating-alert-templates/#objects-and-fields-reference)

[HTML Explorer offline template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-explorer-offline)

[HTML Explorer reconnect template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-explorer-reconnect)

[HTML new asset template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-new-asset-alerts)

[HTML changed asset template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-changed-asset-alerts)

[HTML offline asset template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-offline-asset-alerts)

[HTML assets back online template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-alert-template-for-assets-that-are-back-online)

[HTML asset query template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-asset-query-alerts)

[JSON asset query template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#json-template-for-asset-query-alerts-and-webhooks)

[HTML service query template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-service-query-alerts)

[JSON service query template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#json-template-for-service-query-alerts-and-webhooks)


# HTML template for Explorer offline

## Subject 

```
 Explorer {{event.agent_name}} is offline	
```

## Body

```
<h1>{{event.agent_name}}</h1>

<h2>Explorer Details</h2>
<ul>
<li>
Internal IP: {{event.agent_internal_ip}}
External IP: {{event.agent_external_ip}}
Explorer OS: {{event.agent_os}}
Host UUID: {{event.agent_host_id}}	
Explorer UUID: {{event.agent_id}}	
Explorer last seen (epoch time): {{event.agent_last_seen}}
Exlorer Tags: {{event.agent_tags}}
Explorer version: {{event.agent_version}}
Explorer Organization: {{event.organization_name}}
Explorer Organization UUID: {{event.organization_id}}
Explorer Site: {{event.site_name}}
Explorer Site UUID {{event.site_id}}
</li>
</ul>
```

# HTML template for Explorer reconnect

## Subject 

```
 Explorer {{event.agent_name}} is back online	
```

## Body

```
<h1>{{event.agent_name}}</h1>

<h2>Explorer Details</h2>
<ul>
<li>
Duration offline: {{event.agent_offline_time}}	
Internal IP: {{event.agent_internal_ip}}
External IP: {{event.agent_external_ip}}
Explorer OS: {{event.agent_os}}
Host UUID: {{event.agent_host_id}}	
Explorer UUID: {{event.agent_id}}	
Explorer last seen (epoch time): {{event.agent_last_seen}}
Exlorer Tags: {{event.agent_tags}}
Explorer version: {{event.agent_version}}
Explorer Organization: {{event.organization_name}}
Explorer Organization UUID: {{event.organization_id}}
Explorer Site: {{event.site_name}}
Explorer Site UUID {{event.site_id}}
</li>
</ul>
```

# HTML template for new asset alerts

## Subject

```
{{assets_new}} new asset(s) found during the last scan of {{rule.name}}
```

## Body

```
<h1>{{site.name}}</h1>

<h2>Scan Results</h2>
{{#scan}}
<ul>
<li>{{assets_new}} new assets</li>
</ul>
{{/scan}}

<h2>New assets</h2>
<ul>
{{#report.new}}
<li>{{names}}<br>
    IP(s): {{addresses}}<br>
    OS: {{os}}<br>
    HW: {{hw}}<br>
    Type: {{type}}<br>
    Services: {{service_count}}<br>
    Site: {{site}}<br>
</li>
{{/report.new}}
{{^report.new}}
<li>No new assets were discovered.</li>
{{/report.new}}
</ul>

<p><a href="{{search.url}}">View assets in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

# HTML template for changed asset alerts

## Subject
```
{{assets_changed}} asset(s) have changed since the last scan {{rule.name}}
```

## Body
```
<h1>{{site.name}}</h1>

<h2>Scan Results</h2>
{{#scan}}
<ul>
<li>{{assets_chaged}} changed assets</li>
</ul>
{{/scan}}

<h2>Changed assets</h2>
<ul>
{{#report.changed}}
<li>{{names}}<br>
    IP(s): {{addresses}}<br>
    OS: {{os}}<br>
    HW: {{hw}}<br>
    Type: {{type}}<br>
    Services: {{service_count}}<br>
    Site: {{site}}<br>
</li>
{{/report.changed}}
{{^report.changed}}
<li>No new assets have changed configuration since the last scan.</li>
{{/report.changed}}
</ul>

<p><a href="{{search.url}}">View assets in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

# HTML template for offline asset alerts

## Subject

```
{{assets_offline}} asset(s) were offline during the last scan of {{rule.name}}
```

## Body

```
<h1>{{site.name}}</h1>

<h2>Scan Results</h2>
{{#scan}}
<ul>
<li>{{assets_offline}} offline assets</li>
</ul>
{{/scan}}

<h2>assets offline</h2>
<ul>
{{#report.offline}}
<li>{{names}}<br>
    IP(s): {{addresses}}<br>
    OS: {{os}}<br>
    HW: {{hw}}<br>
    Type: {{type}}<br>
    Services: {{service_count}}<br>
    Site: {{site}}<br>
</li>
{{/report.offline}}
{{^report.offline}}
<li>No assets were offline at the time of the last scan.</li>
{{/report.offline}}
</ul>

<p><a href="{{search.url}}">View offline assets in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

# HTML alert template for assets that are back online

## Subject

```
{{assets_offline}} asset(s) were offline during the last scan of {{rule.name}}
```

## Body

```
<h1>{{site.name}}</h1>


<h2>Scan Results</h2>
{{#scan}}
<ul>
<li>{{assets_online}} online assets</li>
<li>{{assets_offline}} offline assets</li>
<li>{{assets_changed}} modified assets</li>
</ul>
{{/scan}}


<h2>Offline assets are back online</h2>
<ul>
{{#report.online}}
<li>{{names}}<br>
    IP(s): {{addresses}}<br>
    OS: {{os}}<br>
    HW: {{hw}}<br>
    Type: {{type}}<br>
    Services: {{service_count}}<br>
    Site: {{site}}<br>
</li>
{{/report.online}}
{{^report.online}}
<li>No offline devices have come online since last scan.</li>
{{/report.online}}
</ul>

<p><a href="{{search.url}}">View offline assets in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

# HTML template for asset query alerts

## subject

```
{{search.found}} assets match {{rule.name}}
```

## Body

```
<h1>{{organization.name}}</h1>
<h1>{{site.name}}</h1>

<h2>Detected assets</h2>
<ul>
{{#query.assets}}
<li>Asset ID: {{id}}<br>
    Hostname: {{names}}<br>
    IP: {{address}}<br>
    OS: {{os}}<br>
    HW: {{hw}}<br>
    Type: {{type}}<br>
    Service count: {{service_count}}<br>
    Site: {{site}}<br>
</li>
{{/query.assets}}
</ul>

<p><a href="{{search.url}}">View assets in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

# JSON template for asset query alerts and webhooks

## body

```
{
  "organization": {
    "name": "{{organization.name}}",
    "id": "{{organization.id}}"
  },
  "site": {
    "name": "{{site.name}}",
    "id": "{{site.id}}"
  },
  "rule": {
    "action": "{{rule.action}}",
    "event": "{{rule.event}}",
    "id": "{{rule.id}}",
    "name": "{{rule.name}}"
  },
  "query": {
    "count": "{{query.count}}",
    "assets": "{{query.assets}}"
  }
  "search": {
    "url": "{{search.url}}",
    "found": "{{search.found}}"
  }
}
```

# HTML template for service query alerts

## subject

```
{{search.found}} services match {{rule.name}}
```

## Body

```
<h1>{{organization.name}}</h1>
<h1>{{site.name}}</h1>

<h2>Detected assets and services</h2>
<ul>
{{#query.services}}
<li>Asset ID: {{id}}<br>
    Hostname: {{names}}<br>
    IP: {{address}}<br>
    VHost: {{vhost}}<br>
    Port: {{port}}<br>
    Transport: {{transport}}<br>
    Protocol: {{protocol}}<br>
    Summary: {{summary}}<br>
    OS: {{os}}<br>
    HW: {{hw}}<br>
    Type: {{type}}<br>
    Site: {{site}}<br>
    </li>
{{/query.services}}
</ul>

<p><a href="{{search.url}}">View services in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

# JSON template for service query alerts and webhooks


## Body

```
{
  "organization": {
    "name": "{{organization.name}}",
    "id": "{{organization.id}}"
  },
  "site": {
    "name": "{{site.name}}",
    "id": "{{site.id}}"
  },
  "rule": {
    "action": "{{rule.action}}",
    "event": "{{rule.event}}",
    "id": "{{rule.id}}",
    "name": "{{rule.name}}"
  },
  "query": {
    "count": "{{query.count}}",
    "services": "{{query.services}}"
  }
  "search": {
    "url": "{{search.url}}",
    "found": "{{search.found}}"
  }
}
```

