build: fmt generate
	CGO_ENABLED=0 go build -o morningbot main.go

generate:
	go generate ./...

fmt:
	go fmt ./...

lint:
	golangci-lint run
