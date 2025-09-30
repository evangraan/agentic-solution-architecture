PWD=$(pwd)
echo $PWD

if [ "$(basename "$PWD")" != "IaC" ]; then
  echo "Please run from the IaC directory"
  exit 1
fi

LIST=$(ls -1 ../ | grep _agent)
for f in $LIST; do
  echo "Packaging $f"
  cd ../$f
  zip $f.zip *
  cd -
done

terraform plan
if [ "$?" -ne 0 ]; then
  exit 1
fi
terraform apply -auto-approve

echo "Done"
