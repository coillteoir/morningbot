package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/coillteoir/morningbot/ent"
	"github.com/coillteoir/morningbot/ent/player"
	"github.com/goccy/go-yaml"
	_ "github.com/mattn/go-sqlite3"
)

type Config struct {
	ServerName         string
	Timezone           string
	ChannelID          string
	MorningEmoji       rune
	EarlyEmoji         rune
	BadMorningEmoji    rune
	WeatherAPIKey      string
	NewsAPIKey         string
	GoodMorningPhrases []string `yaml:"goodMorningPhrases"`
	GoodMorningGifs    []string
	EasterEggPhrases   map[string]string
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	data, err := os.ReadFile("config/config.yaml")
	if err != nil {
		logger.Error(err.Error())
	}

	config := Config{}
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		logger.Error(err.Error())
	}

	client, err := ent.Open("sqlite3", "file:leaderboard.db?_fk=1")
	if err != nil {
		logger.Error(fmt.Sprintf("failed opening connection to sqlite: %v", err))
	}
	defer client.Close()

	if err := client.Schema.Create(context.Background()); err != nil {
		logger.Error(fmt.Sprintf("failed creating schema resources: %v", err))
	}

	token := os.Getenv("DISCORD_TOKEN")
	session, err := discordgo.New("Bot " + token)
	if err != nil {
		logger.Error(err.Error())
	}

	logger.Info("Logged in")

	session.AddHandler(func(sesh *discordgo.Session, message *discordgo.MessageCreate) {
		content := message.Content
		logger.Info(message.Content)
		newContent := strings.ToLower(content)

		for _, phrase := range config.GoodMorningPhrases {
			if !strings.Contains(phrase, newContent) {
				continue
			}

			err = sesh.MessageReactionAdd(message.ChannelID,
				message.ID,
				"☀️",
			)
			if err != nil {
				logger.Error(err.Error())
			}

			logger.Info(message.Author.ID)
			p, err := client.Player.Query().Where(player.DiscordID(message.Author.ID)).Only(context.Background())
			// found
			if err == nil {
				if err := p.Update().SetScore(p.Score + 1).Exec(context.Background()); err != nil {
					logger.Error(err.Error())
				}
				return
			}
			logger.Info("not found")
			player, err := client.Player.
				Create().
				SetDiscordID(message.Author.ID).SetScore(1).Save(context.Background())
			if err != nil {
				logger.Error(err.Error())
			}
			logger.Info("created player", player)
		}
	})

	err = session.Open()
	if err != nil {
		logger.Error(err.Error())
	}

	sigch := make(chan os.Signal, 1)
	signal.Notify(sigch, os.Interrupt)
	<-sigch

	err = session.Close()
	if err != nil {
		logger.Error(err.Error())
	}
}
