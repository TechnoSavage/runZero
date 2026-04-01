load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_get='get', http_post='post', 'url_encode')
load('uuid', 'new_uuid')

#Change the URL to match your Ivanti Neurons app registration
RUNZERO_CONSOLE = 'https://console.runzero.com'
OPENWEATHERMAP_URL = 'http://api.openweathermap.org'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets, weather_token):
    assets_import = []
    for asset in assets:
        runzero_id = asset.get('id')
        integration_id = str(new_uuid)
        lat_lon = asset.get('attributes', {}).get('geo.latLons', None)
        if lat_lon:
            coordinates = lat_lon.split(',')
            lat = coordinates[0].strip()
            lon = coordinates[1].strip()
        forecast = get_forecast(weather_token, lat, lon)
        #map additional custom attributes
        weather_list = forecast.get('list', [])
        city_data = forecast.get('city', {})
        city_id = city_data.get('id')
        city_name = city_data.get('name')
        city_lat = str(city_data.get('coord', {}).get('lat'))
        city_lon = str(city_data.get('coord', {}).get('lon'))
        country = city_data.get('country')
        population = str(city_data.get('population'))
        timezone = city_data.get('timezone')
        sunrise = city_data.get('sunrise')
        sunset = city_data.get('sunset')
        
        custom_attributes = {
                             'city.id': city_id,
                             'city.name': city_name,
                             'coord.lat': city_lat,
                             'coord.lon': city_lon,
                             'country': country,
                             'population': population,
                             'timezone': timezone,
                             'sunrise': sunrise,
                             'sunset': sunset,
                            }

        for item in weather_list:
            prefix = item.get('dt_txt')
            for k, v in item['main'].items():
                custom_attributes[prefix + '.' + k] = str(v)
            custom_attributes[prefix + '.weather'] = item.get('weather', [])[0].get('main')
            custom_attributes[prefix + '.weatherDescription'] = item.get('weather', [])[0].get('description')
            custom_attributes[prefix + '.windSpeed'] = item.get('wind', {}).get('speed')
            custom_attributes[prefix + '.windDeg'] = item.get('wind', {}).get('deg')
            custom_attributes[prefix + '.windGust'] = item.get('wind', {}).get('gust')
            custom_attributes[prefix + '.visibility'] = item.get('visibility')
            custom_attributes[prefix + '.clouds'] = item.get('clouds', {}).get('all')

        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=runzero_id,
                runZeroID=runzero_id,
                customAttributes=custom_attributes
            )
        )
    return assets_import

def get_assets(export_token):
    url = RUNZERO_CONSOLE + '/api/v1.0/export/org/assets.json'
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + export_token}
    params = {'search': 'has:geo.latLons',
              'fields': 'id, attributes'}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('Failed to retrieve runZero assets from ' + RUNZERO_CONSOLE, 'status code: ' + str(response.status_code))
        return None
    assets = json_decode(response.body)
    return assets

def get_forecast(weather_token, lat, lon):
    url = OPENWEATHERMAP_URL + '/data/2.5/forecast?'
    headers = {}
    params = {'appid': weather_token,
              'lat': lat,
              'lon': lon,
              'units': 'imperial'}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('Failed to retrieve forecast data.', 'status code: ' + str(response.status_code))
        return None
    forecast = json_decode(response.body)
    return forecast

def main(*args, **kwargs):
    export_token = kwargs['access_key']
    weather_token = kwargs['access_secret']
    assets = get_assets(export_token)
    if len(assets) == 0:
        print('No external assets found.')
        return None
    
    # Format asset list for import into runZero
    import_assets = build_assets(assets, weather_token)
    if not import_assets:
        print('No assets to import')
        return None

    return import_assets