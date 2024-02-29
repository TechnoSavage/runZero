[Alert object and field reference](https://www.runzero.com/docs/creating-alert-templates/#objects-and-fields-reference)

[HTML new asset template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-new-asset-alerts)

[HTML offline asset template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-offline-asset-alerts)

[HTML assets back online template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-alert-template-for-assets-that-are-back-online)

[HTML asset query template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-asset-query-alerts)

[HTML service query template](https://github.com/TechnoSavage/runZero/blob/main/example_alert_templates.md#html-template-for-service-query-alerts)


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
<li>{{names}} IP(s):{{addresses}} OS:{{os}} HW:{{hw}} Type:{{type}} Services:{{service_count}}</li>
{{/report.new}}
{{^report.new}}
<li>No new assets were discovered.</li>
{{/report.new}}
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
<li>{{names}} IP(s):{{addresses}} OS:{{os}} HW:{{hw}} Type:{{type}}</li>
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
<li>{{names}} IP(s):{{addresses}} OS:{{os}} HW:{{hw}} Type:{{type}}</li>
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
<li>Asset ID:{{id}} Hostname:{{names}} IP:{{address}} OS:{{os}} Open Ports:{{port}} Protocol:{{protocol}} HW:{{hw}} Type:{{type}}</li>
{{/query.assets}}
</ul>

<p><a href="{{search.url}}">View assets in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
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
<li>Asset ID:{{id}} Hostname:{{names}} IP:{{address}} Summary:{{summary}} Port:{{port}} OS:{{os}} HW:{{hw}} Type:{{type}}</li>
{{/query.services}}
</ul>

<p><a href="{{search.url}}">View services in console</a></p>
<p><a href="{{task.url}}">View the scan results</a></p>
```

