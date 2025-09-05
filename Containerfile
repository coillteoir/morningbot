FROM golang:1.24.5-bullseye

COPY go.mod go.mod
COPY go.sum go.sum

RUN go mod download

COPY ent ent

COPY main.go main.go

RUN go build -o /morningbot main.go

CMD ["/morningbot"]
