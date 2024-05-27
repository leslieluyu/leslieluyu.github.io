for each in *.yaml;
do
	echo $each
	kubectl delete -f $each
done
