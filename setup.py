from setuptools import setup, find_namespace_packages

setup(
    name = 'pulumi-datadog-gcp-integration',
    version = '0.1.0',
    url = 'https://github.com/saiko-tech/pulumi-datadog-gcp-integration',
    description = 'Pulumi package for setting up the DataDog GCP integration and GCP to DataDog log sinks',
    packages = ['pulumi_datadog_gcp_integration'],
    package_dir={
        'pulumi_datadog_gcp_integration': './pulumi/datadog_gcp_integration'
    },
    install_requires=[
        'pulumi>=3.0.0,<4.0.0',
        'pulumi-gcp>=5.0.0,<6.0.0',
        'pulumi-random>=4.2.0,<5.0.0',
        'pulumi-datadog>=4.6.0,<5.0.0'])
