IMG := data-science-pipeline
TAG := 2020.1.22
NAME := pipeline
USER := kaggle
CONFIG := config/sample_lgbm_regression.yml

docker-build:
	make -C docker/ IMG=${IMG} TAG=${TAG}

env:
	docker run --rm -it --init \
	--ipc host \
	--name ${NAME} \
	--volume `pwd`:/app/${NAME} \
	-w /app/${NAME} \
	--user `id -u`:`id -g` \
	--publish 9000:9000 \
	${IMG}:${TAG} /bin/bash

jupyter:
	sudo chown ${USER}:${USER} /home/user/.jupyter
	jupyter lab --port 9000 --ip 0.0.0.0 --NotebookApp.token=

unittest:
	python -m unittest discover -v -s ./test

run:
	python main.py --config ${CONFIG}
