FROM golang:1.25.2 as builder

COPY go.mod go.mod
COPY go.sum go.sum

RUN go mod download

COPY ent ent
COPY cmd/ cmd/

COPY main.go main.go

RUN CGO_ENABLED=0 go build -o /morningbot main.go

FROM alpine

COPY --from=builder /morningbot /morningbot

WORKDIR /root

CMD ["/morningbot"]
