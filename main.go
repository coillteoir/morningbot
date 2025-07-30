package main

import (
	"log"
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
	"github.com/bwmarrin/discordgo"
)

func main() {

	db, err := sql.Open("sqlite3", "./leaderboard.db")	
	if err != nil {
		log.Fatal(err)
	}

	// TODO: orm
	initSql := `
	create table leaderboard (id integer not null primary key, name text, score integer);
	`
	_, err  = db.Exec(initSql)
	if err != nil {
		log.Fatal(err)
	}

	session, err := discordgo.New("nice try")
	if err != nil {
		log.Fatal(err)
	}

	session.AddHandler(func(sesh *discordgo.Session, message *discordgo.MessageCreate) {
		log.Println(message)
	})

	err = session.Open()
	if err != nil {
		log.Fatal(err)
	}
}
