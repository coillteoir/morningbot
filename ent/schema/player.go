package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/field"
	"time"
)

// Player holds the schema definition for the Player entity.
type Player struct {
	ent.Schema
}

// Fields of the Player.
func (Player) Fields() []ent.Field {
	return []ent.Field{
		field.String("discordID").Unique(),
		field.Int("score").Positive(),
		field.Time("last_message").Default(time.Now),
	}
	return nil
}

// Edges of the Player.
func (Player) Edges() []ent.Edge {
	return nil
}
