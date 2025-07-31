package main

import (
	"log"
	"os"
	"os/signal"
	// "database/sql"
	"github.com/bwmarrin/discordgo"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// db, err := sql.Open("sqlite3", "./leaderboard.db")
	// if err != nil {
	// 	log.Fatal(err)
	// }

	// // TODO: orm
	// initSql := `
	// create table leaderboard (id integer not null primary key, name text, score integer);
	// `
	// _, err  = db.Exec(initSql)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	token := os.Getenv("DISCORD_TOKEN")
	session, err := discordgo.New("Bot " + token)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Logged in")

	session.AddHandler(func(sesh *discordgo.Session, message *discordgo.MessageCreate) {
		content := message.Message.Content
		log.Println(message.Message.Content)
		if content == "gm" {
			err = sesh.MessageReactionAdd(message.Message.ChannelID,
				message.Message.ID,
				"☀️",
			)
			if err != nil {
				log.Print(err)
			}
		}
	})

	err = session.Open()
	if err != nil {
		log.Fatal(err)
	}

	sigch := make(chan os.Signal, 1)
	signal.Notify(sigch, os.Interrupt)
	<-sigch

	err = session.Close()
	if err != nil {
		log.Fatal(err)
	}
}
