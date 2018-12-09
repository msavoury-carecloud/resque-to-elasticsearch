# resque-to-elasticsearch
Scrapes resque and stores failed job information in Elasticsearch

# Issues
ssl cert issue. currently failing with following message

```
raise ImproperlyConfigured("Root certificates are missing for certificate "
elasticsearch.exceptions.ImproperlyConfigured: Root certificates are missing for certificate validation. Either pass them in using the ca_certs parameter or install certifi to use it automatically.
```
