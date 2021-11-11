
# Deploying Models to Production with MLflow and AWS (Sagemaker, Lambda function, API Gateway)

This repo show you how to prepare you Machine Learning model for production in AWS with the help of MLflow and AWS Command Line Inteface (AWS CLI).
The image below shows the architecture and technologies used in this project.


<img src="/images/technologies.PNG" alt="technologies"  width=650>


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

* **Create a new AWS AIM User**
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

* **Setup AWS CLI configuration**
    * Be sure you have installed *AWS CLI* and type command in your terminal: `aws configure`.
    * Then you will have to enter your own credentials as follows:
        * **AWS Access Key ID**: go to *IAM*, then Users, and click on your user just created. Select *Security credentials* tab and copy the value of *AWS Access Key ID*
        * **AWS Secret Access Key**: paste this code from your own notes. You have seen this code originally from *Security credentials* of your user.
        * **Default region name**: go to main AWS interface, click on your region, and check which region is activated for you (us-east-1, eu-west-1, and so on).
        * **Default output format**: set it as *json*.

### Step 4. Test if *mlflow* is working good
* Before doing all following steps, we must be sure if our freshly installed *mlflow* service if working good on our local machine. To do it, type the following command in the terminal: `mlflow ui`.
* Open the *mlflow* dashboard on you browser by entering following URL to your *localhost*: ``http://127.0.0.1:5000``. Please keep in mind that this service uses port 5000 on your machine (open the second terminal window on the same working directory before run this command).

You should see mlflow dashboard interface

## Create Machine Learning model for *mlflow*
### Step 1. Adapt your ML training code for mlflow
In order to make out ML code be understandable for mlflow we must do quick changes in model training codes, described in the following steps.
* Copy and paste the full code from train.py (available in this repo).
* Adapt the Python code to track some model metrics in *mlflow* with following changes in code:
```` py
import mlflow
import mlflow.sklearn
````
  
```` py
mlflow.set_experiment("fraude_classification_model")
````
  
```` py
with mlflow.start_run(run_name="Model experiment F") as run:
    mlflow.log_param("num_estimators", num_estimators)
````
  
```` py
    mlflow.sklearn.log_model(rf, "random-forest-model")
````
  
```` py
    # Log model metrics (Recall, F1-Score)
    mlflow.log_metric("Recall", float(metricas['Recall']))
    mlflow.log_metric("F1-Score", float(metricas['F1']))
````
  
```` py
    # close mlflow connection
    run_id = run.info.run_uuid
    experiment_id = run.info.experiment_id
    mlflow.end_run()
    print(mlflow.get_artifact_uri())
    print("runID: %s" % run_id)
````
With the code changes above, we are ready to track recall and F1-score metrics for the model and generate some run artifacts in *mlflow* dashboard.

### Step 2. Run the model and track metrics in mlflow
* Activate the same virtual environment on the second terminal window as we have created in **Step no.1** with the following command: `conda activate deploy_ml` and go to the project folder and run the model training code with `python train.py`.
* Once the train script executed sucessfully, you will be notificated about creation of new experiment in *mlflow*, the metrics, absolute directory path to model artifacts, and `runID`
* Open the browser window again where mlflow service is running on. Refresh the browser window. Then, on the left menu Experiments you will see updated list of experiments ran so far, which includes that one you ran recently in this step (my_classification_model), see the screenshot below.
<img src="/images/mlflow_experiments.PNG" alt="technologies"  width=400>

* Click on the new experiment, and freely navigate through available options to check metric values and other parameters from the experiment.

* Once you entered to your new experiment space, click on the most recent run tagged with Random Forest Experiment Run time tag. Be sure, that on the Artifacts section you are seeing this kind of structured experiment files with filled content for each file. See screenshot below.
<img src="/images/mlflow_artifacts.PNG" alt="technologies"  width=400>
Among the artifact files, there is a conda.yaml file. This is the environment your model needs to run.

## Deploy the model to AWS
### Step 1. Build a Docker Image and push it to AWS ECR
* Open a terminal and activate the deploy_ml environment, got to the artifact directory of selected model run in mlruns folder (in my case I set this directory as: /mlruns/1/54df8f4eb4e149a79f6761ab305ca630/artifacts/random-forest-model), then type and run a command: ``mlflow sagemaker build-and-push-container``.
You will see all processes running in real time in your terminal, as shown in a screenshot below.

If you have set up AWS correctly with the proper permissions, this will build an image locally and push it to your image (name is *mlflow-pyfunc*) registry on AWS.

* Once you finished the previous action without any issues, you should check local Docker Desktop to be sure that everything is well at this moment. Open your Docker Desktop application and go to Images section. You should see two images created. The first one indicates your AWS ECR container image, and the other one is mlflow-pyfunc.

* Check **AWS ECR** repos list. 
* Check image parameters in **AWS ECR** by clicking on ``mlflow-pyfunc`` image repository. On a image properties window you will see the main parameters of your image such as *Image URI*, Size, and other ones.


### Step 2. Deploy image to Sagemaker
**Important**: Before doing all following steps, you should create a special CLI token between your terminal and AWS. For this boto3 package is responsible, and you can do it in very simple way, just by setting your environment variables in your terminal like following:

* Type `AWS_ACCESS_KEY=XXXXXXXXX`, where `XXXXXXXXX` is your *AWS Access Key* for your User in AWS.
* Type `AWS_SECRET_ACCESS_KEY=XXXXXXXXX`, where `XXXXXXXXX` is your *AWS Secret Access Key* for your User in AWS.

* Create a new Python script in your root project directory by terminal command ``touch deploy.py``. This command will create a new file *deploy.py*.
* Write the following script logic in the *deploy.py* you have just created:

```` py
import mlflow.sagemaker as mfs

experiment_id = '1'
run_id = 'XXXXXXXXXXXXXX'
region = 'us-east-2'
aws_id = 'XXXXXXXXXXXXXX'
arn = 'arn:aws:iam::XXXXXXXXXXXXXX:role/sagemaker-full-access-role'
app_name = 'fraude-application'
model_uri = 'mlruns/%s/%s/artifacts/random-forest-model' % (experiment_id, run_id)
tag_id = '1.18.0'

image_url = aws_id + '.dkr.ecr.' + region + '.amazonaws.com/mlflow-pyfunc:' + tag_id

mfs.deploy(app_name=app_name, 
           model_uri=model_uri, 
           region_name=region, 
           mode="create",
           execution_role_arn=arn,
           image_url=image_url)

````
As you can see from the *deploy.py* skeleton code, we will need to get `run_id`, `region`, `aws_id`, ARN for *AmazonSageMakerFullAccess* (`arn`), `model_uri`, and `image_url`. Let's extract these values one by one.

* `experiment_id`:
    * Open the *Mlflow* user interface in http://127.0.0.1:5000.
    * Click on your experiment (for example *fraude_classification_model*).
    * You will see an Experiment ID in the upper side of the screen next to Experiment ID text. Copy the value (in my case it is 1).

* `run_id`:
    * Open the *Mlflow* user interface in http://127.0.0.1:5000.
    * Click on your experiment (for example *fraude_classification_model*).
    * Click on run which has an image to an AWS ECR.
    * On Artifacts section expand the list of artifacts by clicking on an arrow, and select **MLModel**.
    * On the data window on the right, you can see main data about the model. One of these is `run_id`. Copy it.

* `aws_id`:
Get your AWS ID from the terminal by running this command: `aws sts get-caller-identity --query Account --output text`.

* `arn`:
Create the Role for the *SageMakerFullAccess* and grab it's *ARN*.
    * Open **IAM** Dashboard.
    * Click on **Create role**.
    * Select **SageMaker** service from the given list and click **Next: Permissions**.
    * Click **Next: Tags**.
    * Once you completed to create this role, copy Role ARN for further usage (*Role ARN*).
* `region`:
Go to main AWS interface, click on your region, and check which region is activated for you (us-east-1, eu-west-1, and so on).

* `app_name`:
Set any name you want to recognize your application.

* `tag_id`:
This the version of mlflow. Open **AWS ECR**, then open your repository, and copy the value of *Image tag*.

* Open again terminal with activated virtual environment *deploy_ml* and enter run the *deploy.py* Python script with the command: `python deploy.py`.


## Create Lamba Function on AWS
* Go to the Lambda Service and click on **create function**.
* Select the *Author from scratch* option.
* In the Basic information secction:
    * `Function Name`: Put a name (in my case *fraude_prediction*) 
    * `Runtime`: select *python3.9*
    * `Execution role`: select *create a new role with basick lambda permissions*
* Click on **create function**
* Go to *Code Source* section and copy the `lambda_function.py`  (available in this repo). 
The new Role created with the lambda function(fraude_prediction) needs access to the sagemaker endpoint, follow the next steps:

* Open **IAM** Dashboard
* Click on **roles**, and select fraude_prediction role.
* Click on **Attach policies** and type sagemaker then select *AmazonSageMakerFullAccess*

We need to test the lambda function to validate connection with our sagemaker endpoint.

*   Go to the **Lambda Service**
*   Click on **functions** and select *fraude_prediction* .
*   Click on **Configure test event** and pase the code below:
```json
{
  "key1": "value1",
  "data": {
    "columns": [
      "hora",
      "dia",
      "establecimiento_No_definido",
      "ciudad_No_definido",
      "interes_tc_cat_A_<40]",
      "linea_tc_cat_A_<44000]",
      "device_score_1"
    ],
    "index": [9],
    "data": [[22,5,0,1,0,0,0]]
  }
}
```
We might get a `Response 0` in the *Execution Results* tab.

<img src="/images/aws_lambda_test.PNG" alt="technologies"  width=400>



## Create REST Api with AWS Gateway
*   Go to **API Gatway** dashboard and Click on **Create API**
*   In the **REST API** section Click on *Build* and write an *API name* (in my case `fraude_api`)
*   Click on **Actions** and select *Create Method*
*   Select **POST** Method and mark the check box.
*   On the *POST - Setup* go to *Lambda Function* part and write `fraude_prediction` and Click on Ok
*   Click on **Actions** and select *Deploy API*
*   In Deployment stage select *[New Stage]*
*   In Stage name write *fraudemodel* and click on **Deploy**

<img src="/images/aws_API.PNG" alt="technologies"  width=500>



## Use REST API with a simple Webapp using streamlit

- [Demo Web App](https://streamlit-app-challenge.herokuapp.com/)
- [Repo Web App](https://github.com/martinsincu/webapp_challenge)

## Referencias
- [AWS](https://docs.aws.amazon.com/)
- [Mlflow](https://www.mlflow.org/docs/latest/index.html)
- [Docker](https://docs.streamlit.io/)
- [Streamlit](https://docs.docker.com/)


