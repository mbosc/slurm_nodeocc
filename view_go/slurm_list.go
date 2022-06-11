package main

import (
	"fmt"
	"os"

	// "github.com/brianvoe/gofakeit"

	table "github.com/calyptia/go-bubble-table"
	"github.com/charmbracelet/bubbles/stopwatch"
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

// TODO
// - replace stopwatch with pipe reader

type newDataMsg struct {
	Joblets []Joblet
	Jobs    []Job
}

func runPipeReader() tea.Msg {
	Joblets, Jobs := GetDump(os.Getenv("USER")).GetJoblets()
	return newDataMsg{Joblets, Jobs}
}

func fillTable(tbl *table.Model, joblets []Joblet, jobs []Job) {
	rows := make([]table.Row, len(joblets))
	for i := 0; i < len(joblets); i++ {
		rows[i] = table.SimpleRow{
			joblets[i].JobId,
			jobs[i].Name,
			jobs[i].User,
			jobs[i].State,
			jobs[i].Runtime,
			joblets[i].Mem,
			joblets[i].NGpus,
			jobs[i].Reason,
		}
	}
	tbl.SetRows(rows)
}

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

	// fillTable(&tbl)
	sw := stopwatch.NewWithInterval(1e9)

	return model{table: tbl, stopwatch: sw}
}

type model struct {
	table     table.Model
	stopwatch stopwatch.Model
}

func (m model) Init() tea.Cmd {
	return m.stopwatch.Init()
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case newDataMsg:
		fillTable(&m.table, msg.Joblets, msg.Jobs)
		return m, runPipeReader
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
