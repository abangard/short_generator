import boto3
from sagemaker import Session
from sagemaker.huggingface import HuggingFacePredictor

ENDPOINT_NAME = "mlg-hackathon-shots"


def get_sagemaker_predictor():
    # Global Boto3 session
    boto_session = boto3.Session()
    sagemaker_session = Session(boto_session)

    embedding_predictor = HuggingFacePredictor(
        endpoint_name=ENDPOINT_NAME,
        sagemaker_session=sagemaker_session
    )

    return embedding_predictor


if __name__ == "__main__":
    predictor = get_sagemaker_predictor()
    print(predictor.predict({"inputs": "Hello, world!"}))