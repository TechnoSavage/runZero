# HTML template for new device discovery

## Subject

```
{{assets_new}} new devices were detected during the last scan of {{rule.name}}
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