FROM golang

COPY go.mod go.mod
COPY go.sum go.sum

RUN go mod download

COPY main.go main.go

RUN go build -o /morningbot main.go

CMD ["/morningbot"]
