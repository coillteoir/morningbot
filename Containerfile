FROM golang:1.25.2

COPY go.mod go.mod
COPY go.sum go.sum

RUN go mod download

COPY ent ent
COPY cmd/ cmd/

COPY main.go main.go

RUN go build -o /morningbot main.go

CMD ["/morningbot"]
