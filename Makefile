clean:
	docker rm $(docker ps -a -q)
	docker rmi $(docker images -q)

build:
	docker build . -t lab1

run: build
	sudo docker run -it --rm \
		-v ./scripts/output_csv_repos/repos.csv:/app/scripts/output_csv_repos/repos.csv \
		lab1
