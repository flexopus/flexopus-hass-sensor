# Flexopus Sensor for Home Assistant

## Installation

Add this to configuration.yaml:

```yaml
flexopus:
  access_token: '33|ya5eyoWn948dmLSGGjBgqeQEJlFtwwXtIFppmzhm'
  url: "https://tenant.flexopus.de"
  locations: [1, 2, 3]
```

For local development (from docker) we can use
```yaml
  url: "http://host.docker.internal:8000"
```

But in this case we need to manually authenticate tenant (or update the hosts).


## Useful resources
- https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/
- https://aarongodfrey.dev/home%20automation/use-coordinatorentity-with-the-dataupdatecoordinator/
- https://github.com/custom-components/sensor.nintendo_wishlist/tree/main