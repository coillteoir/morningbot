package cmd

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
						Embeds: []*discordgo.MessageEmbed{
							{
								Title: "Good morning",
							},
						},
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

func init() {
	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	// rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.morningbot.yaml)")

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
