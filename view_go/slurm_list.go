package main

import (
	"fmt"
	"os"

	// "github.com/brianvoe/gofakeit"

	table "github.com/calyptia/go-bubble-table"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"golang.org/x/term"
)

func main() {
	err := tea.NewProgram(initialModel(), tea.WithAltScreen()).Start()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

var (
	styleDoc = lipgloss.NewStyle().Padding(1)
)

func initialModel() model {
	w, h, err := term.GetSize(int(os.Stdout.Fd()))
	if err != nil {
		w = 80
		h = 24
	}
	top, right, bottom, left := styleDoc.GetPadding()
	w = w - left - right
	h = h - top - bottom
	tbl := table.New([]string{"ID", "NAME", "USER", "ST", "TIME", "MEM", "GP", "REASON"}, w, h)

	Joblets, Jobs := GetDump().GetJoblets()

	rows := make([]table.Row, len(Joblets))
	for i := 0; i < len(Joblets); i++ {
		rows[i] = table.SimpleRow{
			Joblets[i].JobId,
			Jobs[i].Name,
			Jobs[i].User,
			Jobs[i].State,
			Jobs[i].Runtime,
			Joblets[i].Mem,
			Joblets[i].NGpus,
			Jobs[i].Reason,
		}
	}
	tbl.SetRows(rows)
	return model{table: tbl}
}

type model struct {
	table table.Model
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		top, right, bottom, left := styleDoc.GetPadding()
		m.table.SetSize(
			msg.Width-left-right,
			msg.Height-top-bottom,
		)
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		}
	}

	var cmd tea.Cmd
	m.table, cmd = m.table.Update(msg)
	return m, cmd
}

func (m model) View() string {
	return styleDoc.Render(
		m.table.View(),
	)
}
