# datadog-gcp-integration (Pulumi)

Set up the [DataDog GCP Integration + Log Sink](https://docs.datadoghq.com/integrations/google_cloud_platform/) via Pulumi

## Installation

1. Add the following to your Pulumi project's `requirements.txt`:

```
git+https://github.com/saiko-tech/pulumi-datadog-gcp-integration@cd8296f0e8773d99c534d41f9c7240ba77c09efe#egg=pulumi-datadog-gcp-integration
```

**NOTE: make sure to use an explicit Git SHA like in the above example isstead of `@master` etc. - always do this when linking against dependencies via Git or you will become the victim of a supply chain attack!**

## Usage

```py
import pulumi_datadog_gcp_integration as dd_gcp

monitoring_enable = projects.Service(
    'monitoring-api',
    service='monitoring.googleapis.com')

cloudasset_enable = projects.Service(
    'cloudasset-api',
    service='cloudasset.googleapis.com')

dd_gcp.DataDogGCPIntegration(
    'datadog-gcp-integration',
    enable_log_sink=True,
    opts=ResourceOptions(depends_on=[monitoring_enable, cloudasset_enable]))
```

## Aknowledgements

- https://docs.datadoghq.com/integrations/google_cloud_platform/
- https://github.com/nephosolutions/terraform-google-datadog-integration
