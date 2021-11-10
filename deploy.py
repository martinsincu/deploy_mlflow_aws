import mlflow.sagemaker as mfs

experiment_id = '1'
run_id = '54df8f4eb4e149a79f6761ab305ca630'
region = 'us-east-2'
aws_id = '589948675517'

arn = 'arn:aws:iam::589948675517:role/aws-sagemaker-for-deploy-model'
app_name = 'fraude-application'
model_uri = f'mlruns/{experiment_id}/{run_id}/artifacts/random-forest-model'
tag_id = '1.18.0'


image_url = aws_id + '.dkr.ecr.' + region + '.amazonaws.com/mlflow-pyfunc:' + tag_id


mfs.deploy(app_name,
	model_uri=model_uri,
	region_name=region,
	mode='create',
	execution_role_arn=arn,
	image_url=image_url)