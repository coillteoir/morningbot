package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/coillteoir/morningbot/ent"
	"github.com/coillteoir/morningbot/ent/player"
	"github.com/go-co-op/gocron/v2"
	"github.com/goccy/go-yaml"
	_ "github.com/mattn/go-sqlite3"
)

type Config struct {
	ServerName         string            `yaml:"serverName"`
	Timezone           string            `yaml:"timezone"`
	ChannelID          string            `yaml:"channelID"`
	MorningEmoji       string            `yaml:"morningEmoji"`
	EarlyEmoji         string            `yaml:"earlyEmoji"`
	BadMorningEmoji    string            `yaml:"badMorningEmoji"`
	WeatherAPIKey      string            `yaml:"WeatherAPIKey"`
	NewsAPIKey         string            `yaml:"newsAPIKey"`
	GoodMorningPhrases []string          `yaml:"goodMorningPhrases"`
	GoodMorningGifs    []string          `yaml:"goodMorningGifs"`
	EasterEggPhrases   map[string]string `yaml:"easterEggPhrases"`
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	data, err := os.ReadFile("config/config.yaml")
	if err != nil {
		logger.Error(err.Error())
		os.Exit(1)
	}

	config := Config{}

	err = yaml.Unmarshal(data, &config)
	if err != nil {
		logger.Error(err.Error())
		os.Exit(1)
	}

	client, err := ent.Open("sqlite3", "file:leaderboard.db?_fk=1")
	if err != nil {
		logger.Error(fmt.Sprintf("failed opening connection to sqlite: %v", err))
		os.Exit(1)
	}

	defer client.Close()

	if err := client.Schema.Create(context.Background()); err != nil {
		logger.Error(fmt.Sprintf("failed creating schema resources: %v", err))
		os.Exit(1)
	}

	token := os.Getenv("DISCORD_TOKEN")

	session, err := discordgo.New("Bot " + token)
	if err != nil {
		logger.Error(err.Error())
		os.Exit(1)
	}

	logger.Info("Logged in")

	handleMessage := func(sesh *discordgo.Session, message *discordgo.MessageCreate) {
		content := message.Content
		logger.Info(message.Content)

		newContent := strings.ToLower(content)

		for phrase, emoji := range config.EasterEggPhrases {
			if !strings.Contains(phrase, newContent) {
				continue
			}

			err = sesh.MessageReactionAdd(message.ChannelID,
				message.ID,
				emoji,
			)
			if err != nil {
				logger.Error(err.Error())
			}

			break
		}

		for _, phrase := range config.GoodMorningPhrases {
			if !strings.Contains(phrase, newContent) {
				continue
			}

			currentHour := time.Now().Hour()
			if !(currentHour < 12 && currentHour > 5) {
				break
			}

			err = sesh.MessageReactionAdd(message.ChannelID,
				message.ID,
				"☀️",
			)
			if err != nil {
				logger.Error(err.Error())
			}

			logger.Info(message.Author.ID)
			p, err := client.Player.Query().
				Where(player.DiscordID(message.Author.ID)).
				Only(context.Background())
			// found
			if err == nil {
				err := p.Update().
					SetScore(p.Score + 1).
					SetLastMessage(time.Now()).
					Exec(context.Background())
				if err != nil {
					logger.Error(err.Error())
				}

				return
			}

			logger.Info("player not found")

			player, err := client.Player.
				Create().
				SetDiscordID(message.Author.ID).
				SetScore(1).
				Save(context.Background())
			if err != nil {
				logger.Error(err.Error())
			}

			logger.Info("created player", player)
		}
	}

	session.AddHandler(handleMessage)

	err = session.Open()
	if err != nil {
		logger.Error(err.Error())
	}

	scheduler, err := gocron.NewScheduler()
	if err != nil {
		logger.Error(err.Error())
	}

	_, err = scheduler.NewJob(
		gocron.DailyJob(1,
			gocron.NewAtTimes(
				gocron.NewAtTime(6, 0, 0),
			),
		),
		gocron.NewTask(
			func() {
				session.ChannelMessageSendComplex(
					config.ChannelID,
					&discordgo.MessageSend{
						Embeds: []*discordgo.MessageEmbed{
							{
								Title: "Good morning",
							},
						},
					},
				)
			},
		),
	)

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
