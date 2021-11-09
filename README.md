# Deploying Models to Production with MLflow and AWS (Sagemaker, Lambda function, API Gateway)

This repo show you how to prepare you Machine Learning model for production in AWS with the help of MLflow and AWS Command Line Inteface (AWS CLI).

## Requirements

- AWS Account.
- Docker installed on your local machine.
- Anaconda software to create conda virtual environment.

## Setup the environment
Installing mlflow to your dedicated virtual environment

### Step 1. Prepare your Python Virtual environment

We will create dedicated virtual environment. 
- Create a new conda virtual environment in you working directory with the following command in your terminal: `conda create --name deploy_ml python=3.6`
- Once your virtual environment is sucessfully created, you can easily to activate it with the following command: `conda activate deploy_ml`

### Step 2. Install dependencies in you virtual environment

* Install *mlflow* package into our virtual environment with the following command: `pip install -q mlflow==1.18.0`.
* To run properly the ML model itself we have to install following modules and packages to our virtual environment:
    * Pandas: `pip install pandas`.
    * Scikit-learn: `pip install -U scikit-learn`.
    * AWS Command Line Interface (AWS CLI): `pip install awscli --upgrade --user`.
    * Boto3: `pip install boto3`.

### Step 3. Setup AWS IAM User and AWS CLI configuration

* Create a new AWS AIM User
    * Open **Identity and Access management (IAM) dashboard**.
    * Click on **Users**.
    * Click **Add users** on the right side of the screenshot.
    * Set the *User name* and mark *Programmatic access* tick below.
    * Click on **Create group** as the part of *Add user to group* option.
    * Type a group name you want to assign to your IAM User.
    * From the list below select following policies:
        * AmazonSageMakerFullAccess.
        * AmazonEC2ContainerRegistryFullAccess.
    * Click on **Create group**, then the current *Policies* window will be closed.
    * Click on **Next: Tags**.
    * Click on **Next: Review**.
    * Click on **Create user**.
    * You will get a notification about sucessfully created new User on AWS IAM.
    **Important.** Keep safe you credentials on your own notes. This step is only one occasion you see AWS Secret Access Key. Rewrite it carefully.