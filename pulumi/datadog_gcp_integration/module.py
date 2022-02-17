import json, base64
import pulumi
from pulumi.output import Output
from pulumi.resource import ComponentResource, ResourceOptions
import pulumi_gcp as gcp
import pulumi_datadog as datadog
import pulumi_random

class GCPLogSinkToDataDog(ComponentResource):
    def __init__(
            self,
            name: str,
            opts: ResourceOptions = None):
        super().__init__('datadog_gcp_integration:index:GCPLogSinkToDataDog', name, None, opts)

        topic = gcp.pubsub.Topic(
            f'{name}-topic',
            name='export-logs-to-datadog',
            opts=ResourceOptions(parent=self))

        dd_api_key = pulumi.Config(name='datadog').require('apiKey')

        push_to_dd = gcp.pubsub.Subscription(
            f'{name}-subscription',
            name='export-logs-to-datadog.push-to-dd',
            topic=topic.id,
            push_config=gcp.pubsub.SubscriptionPushConfigArgs(
                push_endpoint=f'https://gcp-intake.logs.datadoghq.eu/api/v2/logs?dd-api-key={dd_api_key}&dd-protocol=gcp'),
            expiration_policy=gcp.pubsub.SubscriptionExpirationPolicyArgs(
                ttl=''),
            retry_policy=gcp.pubsub.SubscriptionRetryPolicyArgs(
                minimum_backoff='10s',
                maximum_backoff='600s'),
            opts=ResourceOptions(parent=self))

        project = gcp.organizations.get_project()
        pubsub_sa = f'serviceAccount:service-{project.number}@gcp-sa-pubsub.iam.gserviceaccount.com'

        gcp.pubsub.SubscriptionIAMBinding(
            f'{name}-subscriber-ack',
            subscription=push_to_dd.id,
            members=[pubsub_sa],
            role='roles/pubsub.subscriber',
            opts=ResourceOptions(parent=self))

        log_sink = gcp.logging.ProjectSink(
            f'{name}-log-sink',
            name='export-logs-to-datadog',
            destination=Output.concat('pubsub.googleapis.com/', topic.id),
            unique_writer_identity=True,
            opts=ResourceOptions(parent=self, depends_on=[push_to_dd]))

        gcp.pubsub.TopicIAMMember(
            f'{name}-log-sink-pubsub-publisher',
            topic=topic.id,
            role='roles/pubsub.publisher',
            member=log_sink.writer_identity,
            opts=ResourceOptions(parent=self))


class DataDogGCPIntegration(ComponentResource):
    def __init__(
            self,
            name: str,
            enable_log_sink: bool = False,
            opts: ResourceOptions = None):
        super().__init__('datadog_gcp_integration:index:DataDogGCPIntegration', name, None, opts)

        suffix = pulumi_random.RandomString(
            f'{name}-gcp-sa-suffix',
            length=3,
            min_lower=3,
            opts=ResourceOptions(parent=self))

        gcp_sa = gcp.serviceaccount.Account(
            f'{name}-gcp-sa',
            account_id=Output.concat('datadog-integration-', suffix.result),
            description='DataDog GCP Integration SA',
            opts=ResourceOptions(parent=self))

        roles = [
            'roles/cloudasset.viewer',
            'roles/compute.viewer',
            'roles/container.viewer',
            'roles/monitoring.viewer',
        ]

        iam_members = []

        for role in roles:
            member = gcp.projects.IAMMember(
                f'{name}-gcp-sa-role-{role}',
                role=role,
                member=gcp_sa.email.apply(lambda email: f'serviceAccount:{email}'),
                opts=ResourceOptions(parent=self))

            iam_members.append(member)

        gcp_sa_key = gcp.serviceaccount.Key(
            f'{name}-gcp-sa-key',
            service_account_id=gcp_sa.name,
            opts=ResourceOptions(parent=self))

        gcp_sa_pk = gcp_sa_key.private_key.apply(lambda k: json.loads(base64.b64decode(k)))

        gcp_integration = datadog.gcp.Integration(
            f'{name}-datadog-gcp-integration',
            client_email=gcp_sa_pk.apply(lambda k: k['client_email']),
            client_id=gcp_sa_pk.apply(lambda k: k['client_id']),
            private_key=gcp_sa_pk.apply(lambda k: k['private_key']),
            private_key_id=gcp_sa_pk.apply(lambda k: k['private_key_id']),
            project_id=gcp_sa_pk.apply(lambda k: k['project_id']),
            opts=ResourceOptions(parent=self, depends_on=iam_members))

        if enable_log_sink:
            GCPLogSinkToDataDog(
                f'{name}-export-gcp-logs-to-datadog',
                opts=ResourceOptions(parent=self, depends_on=[gcp_integration]))
