package main

import (
	"context"
	"log"
	"os"
	"os/signal"

	"github.com/bwmarrin/discordgo"
	"github.com/coillteoir/morningbot/ent"
	"github.com/coillteoir/morningbot/ent/player"
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

			log.Println(message.Author.ID)
			p, err := client.Player.Query().Where(player.DiscordID(message.Author.ID)).Only(context.Background())
			if err != nil {
				log.Println("not found")
			} else {
				if err := p.Update().SetScore(p.Score + 1).Exec(context.Background()); err != nil {
					log.Print(err)
				}
				return
			}
			log.Println(p)
			player, err := client.Player.
				Create().
				SetDiscordID(message.Author.ID).SetScore(1).Save(context.Background())
			if err != nil {
				log.Print(err)
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
