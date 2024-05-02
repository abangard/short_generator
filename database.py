# Create OpenSearch client

from opensearchpy import OpenSearch
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

os_host = "search-mlg-hackathon-shots-os-ph3gnwu3m72nopzvjsy4u3sudu.us-east-1.es.amazonaws.com"
os_auth = ('admin', 'Admin@123')


def get_opensearch_client():
    return OpenSearch(
        hosts=[{'host': os_host, 'port': 443}],
        http_auth=os_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )
