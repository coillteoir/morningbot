package main

import (
	"context"
	"log"
	"os"
	"os/signal"

	"github.com/bwmarrin/discordgo"
	"github.com/coillteoir/morningbot/ent"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	client, err := ent.Open("sqlite3", "file:leaderboard.db?_fk=1")
	if err != nil {
		log.Fatalf("failed opening connection to sqlite: %v", err)
	}
	defer client.Close()

	if err := client.Schema.Create(context.Background()); err != nil {
		log.Fatalf("failed creating schema resources: %v", err)
	}

	token := os.Getenv("DISCORD_TOKEN")
	session, err := discordgo.New("Bot " + token)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Logged in")

	session.AddHandler(func(sesh *discordgo.Session, message *discordgo.MessageCreate) {
		content := message.Content
		log.Println(message.Content)
		if content == "gm" {
			err = sesh.MessageReactionAdd(message.ChannelID,
				message.Message.ID,
				"☀️",
			)
			if err != nil {
				log.Print(err)
			}
			player, err := client.Player.
				Create().
				SetDiscordID(message.Author.ID).SetScore(1).Save(context.Background())
			if err != nil {
				log.Fatal(err)
			}
			log.Println("created player", player)
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
