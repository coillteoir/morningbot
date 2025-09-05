build: fmt generate
	go build -race -o morningbot main.go

generate:
	go generate ./...

fmt:
	go fmt ./...

lint:
	golangci-lint run
