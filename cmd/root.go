package cmd

import (
	"context"
	"database/sql"
	"database/sql/driver"
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
	"modernc.org/sqlite"

	"github.com/spf13/cobra"
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

// keyConfigured reports whether an API key has been supplied.
func keyConfigured(key string) bool {
	return strings.TrimSpace(key) != ""
}

// buildMorningEmbeds builds the embeds for the scheduled greeting message.
// The greeting is always included; news and weather are only appended when
// their API keys are configured, so a missing or invalid key only removes
// that section instead of blocking the whole message (issue #49).
func buildMorningEmbeds(cfg Config, logger *slog.Logger) []*discordgo.MessageEmbed {
	embeds := []*discordgo.MessageEmbed{
		{
			Title: "Good morning",
		},
	}

	if news, err := fetchNewsEmbed(cfg); err != nil {
		logger.Warn("skipping news in morning message", "err", err)
	} else if news != nil {
		embeds = append(embeds, news)
	}

	if weather, err := fetchWeatherEmbed(cfg); err != nil {
		logger.Warn("skipping weather in morning message", "err", err)
	} else if weather != nil {
		embeds = append(embeds, weather)
	}

	return embeds
}

// fetchNewsEmbed fetches the latest news as an embed. It returns an error when
// the news API key is not configured so the caller can degrade gracefully
// instead of failing the whole message.
func fetchNewsEmbed(cfg Config) (*discordgo.MessageEmbed, error) {
	if !keyConfigured(cfg.NewsAPIKey) {
		return nil, fmt.Errorf("news API key not configured")
	}
	// Wire up a real news fetch using cfg.NewsAPIKey here (issue #49).
	return nil, nil
}

// fetchWeatherEmbed fetches the current weather as an embed. It returns an
// error when the weather API key is not configured so the caller can degrade
// gracefully instead of failing the whole message.
func fetchWeatherEmbed(cfg Config) (*discordgo.MessageEmbed, error) {
	if !keyConfigured(cfg.WeatherAPIKey) {
		return nil, fmt.Errorf("weather API key not configured")
	}
	// Wire up a real weather fetch using cfg.WeatherAPIKey here (issue #49).
	return nil, nil
}

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "morningbot",
	Short: "A brief description of your application",
	Long: `A longer description that spans multiple lines and likely contains
examples and usage of using your application. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	RunE: func(cmd *cobra.Command, args []string) error {
		logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

		data, err := os.ReadFile("config/config.yaml")
		if err != nil {
			logger.Error("opening config file:", err)
			return err
		}

		config := Config{}

		err = yaml.Unmarshal(data, &config)
		if err != nil {
			logger.Error("parsing config yaml:", err)
			return err
		}

		err = os.Setenv("TZ", config.Timezone)
		if err != nil {
			logger.Error("setting timezone env:", err)
			return err
		}

		setUpDriver()

		client, err := ent.Open("sqlite3", "file:leaderboard.db?_fk=1")
		if err != nil {
			logger.Error(fmt.Sprintf("failed opening connection to sqlite: %v", err))
			return err
		}

		defer client.Close()

		if err := client.Schema.Create(context.Background()); err != nil {
			logger.Error("failed creating schema resources:", err)
			return err
		}

		token := os.Getenv("DISCORD_TOKEN")

		session, err := discordgo.New("Bot " + token)
		if err != nil {
			logger.Error("authenticating morningbot", err)
			return err
		}

		logger.Info("Logged in")

		handleMessage := func(sesh *discordgo.Session, message *discordgo.MessageCreate) {
			content := message.Content
			logger.Info(message.Content)

			//Easter Egg Phrases Checker
			newContent := strings.ToLower(content)

			for phrase, emoji := range config.EasterEggPhrases {
				if !strings.Contains(newContent, phrase) {
					continue
				}

				err = sesh.MessageReactionAdd(message.ChannelID,
					message.ID,
					emoji,
				)
				if err != nil {
					logger.Error("easter egg reaction", err)
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
						logger.Error("cannot update player score", err)
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
					logger.Error("creating player", err)
				}

				logger.Info("created player", player)
			}
		}

		session.AddHandler(handleMessage)

		err = session.Open()
		if err != nil {
			logger.Error("starting discord session", err)
		}

		logger.Info("scheduling leaderboard")

		scheduler, err := gocron.NewScheduler()
		if err != nil {
			logger.Error("creating leaderboard sheduler", err)
		}

		leaderboardSchedule := gocron.DailyJob(1, gocron.NewAtTimes(gocron.NewAtTime(6, 0, 0)))
		leaderboardTask := gocron.NewTask(
			func() error {
				_, err := session.ChannelMessageSendComplex(
					config.ChannelID,
					&discordgo.MessageSend{
						Embeds: buildMorningEmbeds(config, logger),
					},
				)
				if err != nil {
					return err
				}
				return nil
			},
		)
		_, err = scheduler.NewJob(
			leaderboardSchedule,
			leaderboardTask,
		)
		if err != nil {
			logger.Error("adding leaderboard to schedule", err)
		}

		sigch := make(chan os.Signal, 1)
		signal.Notify(sigch, os.Interrupt)
		<-sigch

		err = session.Close()
		if err != nil {
			logger.Error(err.Error())
			return err
		}
		return nil
	},
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

type sqlite3Driver struct {
	*sqlite.Driver
}

type sqlite3DriverConn interface {
	Exec(string, []driver.Value) (driver.Result, error)
}

func (d sqlite3Driver) Open(name string) (conn driver.Conn, err error) {
	conn, err = d.Driver.Open(name)
	if err != nil {
		return
	}
	_, err = conn.(sqlite3DriverConn).Exec("PRAGMA foreign_keys = ON;", nil)
	if err != nil {
		_ = conn.Close()
	}
	return
}

func setUpDriver() {
	sql.Register("sqlite3", sqlite3Driver{Driver: &sqlite.Driver{}})
}

func init() {
	rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
