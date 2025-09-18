build: fmt generate
	go build -o morningbot main.go

generate:
	go generate ./...

fmt:
	go fmt ./...

lint:
	golangci-lint run
