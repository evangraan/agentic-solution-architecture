# Introduction

This repository comprises an agentic solution on AWS bedrock that bootstraps a Solution Architect's work when interfacing with software solutions and teams. This demo shows how to run AI agents locally, without a paywall or the usual cloud concerns. For this POC I used a Macbook Pro.

Note: this demo is self-referential / recursive. If you open up the bedrock architecturl component, you see something like this architecture (except the bedrock proxy would not be there) And if you want to orchestrate and use bedrock in your own solutions, then you see the architecture as it is, with bedrock as an api (the proxy in this demo.)

Think GNU (GNU's not unix) as a recursive acronym analogy. If none of this makes sense, just use bedrock out of the box in AWS.

# Containerisation

Avoid issues with docker, docker desktop and rancher on Macbook, by using podman:

```
brew install podman
```

# Ollama setup

On the mac, do:

```
brew install ollama
ollama serve
ollama pull mistral
```
Test:

Use:

```
./ask_ollama.sh "Say hello"
```

or

```
curl http://localhost:11434/api/generate \
  -d '{
    "model": "mistral",
    "prompt": "Say hello"
  }'
```

# Bedrock runtime (localstack)
Bedrock is expensive, a custom model racks up 100 - 200 USD per day (8 hours active with 8 billion parameter model).
In order to make bedrock POCs accessible, run it in a localstack docker container (backed by llama)

In my case, I prefer podman to avoid docker issues on my mac. Localstack requires docker support in order to run lambdas. It needs access to /var/run/docker.sock which Rancher desktop does not expose and at the time of
this writing my company did not support Docker desktop. As such, localstack needs to run inside podman itself. In order for localstack and docker to be installed in podman, the podman VM needs to be writeable. Use lima (and limactl) to create a writeable Ubuntu podman VM. Ensure podman-ubuntu.yaml has the correct chip architecture (arch) configured for your macbook.

Avoid any system permissions errors:

```
export NEWTEMPDIR="$(mktemp -d -t agentic.XXXXXX)"
export TMP="$NEWTEMPDIR"
export TMPDIR="$NEWTEMPDIR"
export TMP_DIR="$NEWTEMPDIR"
export TEMP="$NEWTEMPDIR"
export TEMPDIR="$NEWTEMPDIR"
```

Start up podman:

```
brew install lima
limactl start --name=podman-ubuntu podman-ubuntu.yaml

limactl shell podman-ubuntu
sudo apt update && sudo apt upgrade -y 
sudo apt-get install -y ca-certificates
sudo timedatectl set-ntp true
```

If your company uses Netskope as intermediary and so the Netskope CA cert needs to be added to the Ubuntu CA store. Copy (or vi) the Netskope .pem onto the podman VM, then:

```
sudo cp netskope.pem /usr/local/share/ca-certificates/netskope-ca.crt
sudo update-ca-certificates
```


Install docker:
```
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

Optional: install support for chipset architecture emulation (required on arm64 chipset macs)
```
sudo apt-get install -y qemu-user-static
sudo docker run --rm --privileged tonistiigi/binfmt --install all
```

Install openssh for access and tunneling:
```
sudo apt install -y openssh-server
```

Update ```/etc/ssh/sshd_config``` to support both ports 22 and 3022

```sudo reboot```

Copy your public SSH key to /root/.ssh/authorized_keys on the podman instance
Set up a reverse tunnel. The bedrock proxy will run on the mac port 9001. The reverse tunnel will map port 11435 on the podman instance
to port 9001 on the mac. Then point the agent at port 11435 on localhost (podman) in docker. 

```
ssh -N -R 11435:127.0.0.1:9001 -i ~/.ssh/id_ed25519 -p 3022 root@localhost
```

Run localstack with support for the services required in this POC. Ensure the docker architecture (--platform) matches the mac chipset (the setting below is for M1):
```
sudo docker pull localstack/localstack:latest
```

On Intel macs:
```
sudo docker run --name localstack --rm -it -p 4566:4566 -p 4510-4559:4510-4559 -e SERVICES=iam,lambda,s3,stepfunctions,apigateway,events -v /var/run/docker.sock:/var/run/docker.sock -e LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT=30 -e DEBUG=1 -e LS_LOG=trace localstack/localstack:latest
```

On arm64 macs:
```
sudo docker run --platform linux/arm64 --name localstack --rm -it -p 4566:4566 -p 4510-4559:4510-4559 -e SERVICES=iam,lambda,s3,stepfunctions,apigateway,events -v /var/run/docker.sock:/var/run/docker.sock -e LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT=30 -e DEBUG=1 -e LS_LOG=trace localstack/localstack:latest
```


Configure AWS to use localstack:
```
~/.aws/config

[profile localstack]
region=us-east-1
output=json
endpoint_url=http://localhost:4566

~/.aws/credentials
[localstack]
AWS_ACCESS_KEY_ID="test"
AWS_SECRET_ACCESS_KEY = "test"
```

# Environment tools

The full solution is bootstrapped and deployed using terraform and AWS CLI v2 with python 3.13.* in a venv
```
% terraform --version
Terraform v1.13.2
on darwin_amd64
+ provider registry.terraform.io/hashicorp/archive v2.7.1
+ provider registry.terraform.io/hashicorp/aws v6.13.0
+ provider registry.terraform.io/hashicorp/time v0.13.1
% aws --version      
aws-cli/2.30.2 Python/3.13.7 Darwin/24.6.0 exe/x86_64
% python -V
Python 3.13.7
```
The languages of choice are plantUML and python

# Python proxy
Run the python proxy in a venv environment in the podman VM.
Note: update run_proxy.sh to set REQUESTS_CA_BUNDLE to the path where you have the Netskope PEM on your machine.

```
cd bedrock_proxy
python3 -m venv venv
source venv/bin/activate
./run_proxy.sh
```

Test in a different shell:
```
cd bedrock_proxy
./ask_proxy.sh "Say hello"
```

# QDrant vector database
Run qdrant in podman and chunk an example standards document into the vector database:

Download qdrant for mac from: https://github.com/qdrant/qdrant/releases

```
chmod +x ~/Downloads/qdrant
xattr -d com.apple.quarantine ~/Downloads/qdrant
~/Downloads/qdrant
```

Ingest the example PDF knowledgebase:

```
cd rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ingest_pdf_to_qdrant.py
```

# IaC

Ensure in main.tf that the endpoints point to the localstack variables.

```
cd IaC
./deploy.sh
```

or

```
cd IaC
terraform init
terraform plan
terraform apply
```

Each lambda has a test script in its directory. To test end-to-end:

```
cd step_function
./test_step_function.sh
```

# S3 / DynamoDB / RDS / Cloudwatch state storage

For audit and debugging purposes, ideally each agent's states should be stored somewhere. My original design was
to do this in S3, how-ever at the time of this writing, there is a localstack bug with the latest terraform aws provider. The provider tries to check existence using s3 HEAD / which localstack does not support. Reverting to an older provider causes bedrock and python to regress etc. This may be fixed in future.

At such time, update iam.tf with S3 policies, create a lambda layer that agents can use to write their request and response data, use the step function execution uuid appended with the agent name as the object name and store to S3.

# Deploying to AWS bedrock proper

Update your AWS CLI configuration for actual deployment.

Write and run a script that replaces us-east-1 and 000000000000 with the actual region and account ID in all .tf and .json files recursively, then run deploy.sh

# Cleaning up

```
terradorm destroy
limactl stop podman-ubuntu
limactl delete podman-ubuntu
```
